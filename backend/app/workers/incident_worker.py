from app.db.database import SessionLocal
from app.models.incident import Incident
from app.models.volunteer import Volunteer          
from app.models.notification import Notification    
from app.models.user import User                    
from app.agents.triage_agent import run_triage

def process_incident(incident_id: int) -> None:
    """
    Job 1 — triggered on incident creation.
    Responsibility: triage only.
    After triage done → enqueues Job 2 (assign_volunteer).
    """
    db = SessionLocal()
    try:
        incident = db.query(Incident).filter(
            Incident.id == incident_id
        ).first()

        if not incident:
            print(f"ERROR: Incident {incident_id} not found")
            return

        # guard against duplicate execution
        if incident.status not in ("open",):
            print(f"Skipping — incident {incident_id} already processing")
            return

        # ── Triage ───────────────────────────────────────────────
        incident.status = "triaging"
        db.commit()

        try:
            triage = run_triage(
                incident_text=incident.description,
                incident_type=incident.type
            )
            incident.severity = triage["severity"]
            incident.confidence = triage["confidence"]
            incident.reasoning = triage["reasoning"]
            incident.rag_used = "yes" if triage.get("rag_used") else "no"
            incident.fallback_used = triage.get("fallback_used", False)
            db.commit()
            print(f"Triage done: incident {incident_id} → {triage['severity']}")
        except Exception as e:
            print(f"WARNING: Triage failed for {incident_id}: {e}")
            incident.severity = "High"
            incident.confidence = 0.0
            incident.reasoning = "Triage failed — defaulting to High"
            incident.fallback_used = True   # ← always True when exception
            db.commit()

        # ── Enqueue Job 2 ─────────────────────────────────────────
        incident.status = "searching"
        db.commit()

        from app.workers.queues import assignment_queue
        from app.workers.assignment_worker import assign_volunteer
        assignment_queue.enqueue(
            assign_volunteer,
            incident_id,
            job_timeout=120
        )
        

    except Exception as e:
        print(f"ERROR in process_incident {incident_id}: {e}")
        try:
            incident.status = "open"
            db.commit()
        except Exception:
            pass
    finally:
        db.close()