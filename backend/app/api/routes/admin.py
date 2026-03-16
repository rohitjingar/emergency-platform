from fastapi import APIRouter, Depends, HTTPException
from sqlalchemy.orm import Session
from sqlalchemy import func
from pydantic import BaseModel
from app.db.database import get_db
from app.core.dependencies import require_role
from app.models.incident import Incident
from app.models.volunteer import Volunteer
from app.models.user import User

router = APIRouter(prefix="/admin", tags=["Admin"])

REVIEW_CONFIDENCE_THRESHOLD = 0.70

# ── Schemas ──────────────────────────────────────────

class OverrideRequest(BaseModel):
    new_severity: str
    reason: str

# ── Helpers ───────────────────────────────────────────

def _get_action_impact(status: str) -> str:
    """Tell admin what will happen if they override."""
    impacts = {
        "searching":          "severity_used_for_next_match",
        "pending_assignment": "volunteer_notified_of_change",
        "assigned":           "volunteer_notified_of_change",
        "triaging":           "severity_updated_before_assignment",
        "open":               "severity_updated_before_assignment",
    }
    return impacts.get(status, "severity_updated")

# ── Review Queue ─────────────────────────────────────

@router.get("/review-queue")
def get_review_queue(
    db: Session = Depends(get_db),
    current_user: dict = Depends(require_role(["admin"]))
):
    """
    Returns all incidents where AI confidence < 70%.
    Shows action_impact so admin knows what override will do.
    Excludes resolved and failed — nothing to act on.
    """
    incidents = db.query(Incident).filter(
        Incident.confidence < REVIEW_CONFIDENCE_THRESHOLD,
        Incident.confidence.isnot(None),
        Incident.status.notin_(["resolved", "failed"])
    ).order_by(Incident.confidence.asc()).all()

    return {
        "review_queue": [
            {
                "incident_id": inc.id,
                "type": inc.type,
                "description": inc.description,
                "severity": inc.severity,
                "confidence": inc.confidence,
                "reasoning": inc.reasoning,
                "status": inc.status,
                "assigned_volunteer_id": inc.assigned_volunteer_id,
                "assignment_attempts": inc.assignment_attempts,
                "created_at": inc.created_at,
                "action_impact": _get_action_impact(inc.status)
            }
            for inc in incidents
        ],
        "count": len(incidents),
        "threshold": REVIEW_CONFIDENCE_THRESHOLD
    }

# ── Approve ───────────────────────────────────────────

@router.patch("/review-queue/{incident_id}/approve")
def approve_decision(
    incident_id: int,
    db: Session = Depends(get_db),
    current_user: dict = Depends(require_role(["admin"]))
):
    """
    Admin confirms AI severity decision is correct.
    Logs approval — no change to severity or assignment.
    """
    incident = db.query(Incident).filter(
        Incident.id == incident_id
    ).first()

    if not incident:
        raise HTTPException(status_code=404, detail="Incident not found")

    if incident.confidence is None:
        raise HTTPException(
            status_code=400,
            detail="Incident has no AI decision to approve"
        )

    incident.reasoning = (
        f"{incident.reasoning or ''} "
        f"[APPROVED by admin user_id={current_user['sub']}]"
    ).strip()
    db.commit()

    return {
        "message": "Decision approved",
        "incident_id": incident_id,
        "severity": incident.severity,
        "confidence": incident.confidence,
        "status": incident.status
    }

# ── Override ──────────────────────────────────────────

@router.patch("/review-queue/{incident_id}/override")
def override_decision(
    incident_id: int,
    data: OverrideRequest,
    db: Session = Depends(get_db),
    current_user: dict = Depends(require_role(["admin"]))
):
    """
    Admin overrides AI severity decision.
    If volunteer already assigned/pending — notifies them of change.
    Logs original severity + reason for full audit trail.
    """
    valid_severities = {"Critical", "High", "Medium", "Low"}
    if data.new_severity not in valid_severities:
        raise HTTPException(
            status_code=400,
            detail=f"Invalid severity. Must be one of: {valid_severities}"
        )

    incident = db.query(Incident).filter(
        Incident.id == incident_id
    ).first()

    if not incident:
        raise HTTPException(status_code=404, detail="Incident not found")

    if incident.status in ("resolved", "failed"):
        raise HTTPException(
            status_code=400,
            detail=f"Cannot override a {incident.status} incident"
        )

    original_severity = incident.severity

    # update severity
    incident.severity = data.new_severity
    incident.reasoning = (
        f"{incident.reasoning or ''} "
        f"[OVERRIDDEN by admin user_id={current_user['sub']}: "
        f"{original_severity} → {data.new_severity}. Reason: {data.reason}]"
    ).strip()
    db.commit()

    # notify volunteer if already assigned or pending
    volunteer_notified = False
    if incident.assigned_volunteer_id and incident.status in (
        "assigned", "pending_assignment"
    ):
        volunteer = db.query(Volunteer).filter(
            Volunteer.id == incident.assigned_volunteer_id
        ).first()

        if volunteer:
            from app.services.notification_service import create_notification
            create_notification(
                db=db,
                user_id=volunteer.user_id,
                notification_type="severity_upgraded",
                message=(
                    f"Severity for incident #{incident_id} has been updated "
                    f"from {original_severity} to {data.new_severity} by admin. "
                    f"Reason: {data.reason}"
                ),
                incident_id=incident_id
            )
            volunteer_notified = True

    return {
        "message": "Severity overridden",
        "incident_id": incident_id,
        "original_severity": original_severity,
        "new_severity": data.new_severity,
        "reason": data.reason,
        "status": incident.status,
        "volunteer_notified": volunteer_notified
    }

# ── Analytics ─────────────────────────────────────────

@router.get("/review-queue/stats")
def get_review_stats(
    db: Session = Depends(get_db),
    current_user: dict = Depends(require_role(["admin"]))
):
    """
    AI decision quality metrics.
    These numbers go directly into resume bullet 4:
    override_rate, avg_confidence, review_rate.
    """
    total = db.query(func.count(Incident.id)).filter(
        Incident.confidence.isnot(None)
    ).scalar() or 0

    needs_review = db.query(func.count(Incident.id)).filter(
        Incident.confidence < REVIEW_CONFIDENCE_THRESHOLD,
        Incident.confidence.isnot(None)
    ).scalar() or 0

    avg_confidence = db.query(func.avg(Incident.confidence)).filter(
        Incident.confidence.isnot(None)
    ).scalar()

    overridden = db.query(func.count(Incident.id)).filter(
        Incident.reasoning.like("%OVERRIDDEN%")
    ).scalar() or 0

    approved = db.query(func.count(Incident.id)).filter(
        Incident.reasoning.like("%APPROVED%")
    ).scalar() or 0

    override_rate = round(overridden / total * 100, 1) if total > 0 else 0
    review_rate = round(needs_review / total * 100, 1) if total > 0 else 0

    return {
        "total_incidents": total,
        "needs_review": needs_review,
        "review_rate_percent": review_rate,
        "avg_confidence": round(float(avg_confidence), 3) if avg_confidence else 0,
        "overridden": overridden,
        "approved": approved,
        "override_rate_percent": override_rate,
        "confidence_threshold": REVIEW_CONFIDENCE_THRESHOLD
    }
    

@router.get("/circuit-breaker")
def get_circuit_breaker_status(
    current_user: dict = Depends(require_role(["admin"]))
):
    """Circuit breaker status — is LLM API healthy?"""
    from app.core.circuit_breaker import get_circuit_status
    return get_circuit_status()