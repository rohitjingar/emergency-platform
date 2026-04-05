# app/workers/timeout_worker.py
from datetime import datetime, timezone, timedelta
from sqlalchemy import or_
from app.db.database import SessionLocal
from app.models.incident import Incident
from app.models.volunteer import Volunteer          
from app.models.notification import Notification   
from app.models.user import User                  
from app.services.matching_service import (
    blacklist_volunteer_timedout,
    is_incident_enqueued,
    mark_incident_enqueued
)

def check_timed_out_assignments() -> None:
    db = SessionLocal()
    try:
        now = datetime.now(timezone.utc)
        from app.workers.queues import assignment_queue
        from app.workers.assignment_worker import assign_volunteer

        # ── Case 1: pending_assignment > 60s (volunteer didn't respond) ──
        cutoff = now - timedelta(seconds=60)
        stale = db.query(Incident).filter(
            Incident.status == "pending_assignment",
            Incident.assigned_at < cutoff,
            Incident.assigned_at.isnot(None)
        ).all()

        if stale:
            print(f"Timeout worker: {len(stale)} timed out assignments")
            for incident in stale:
                # always blacklist timed-out volunteer first
                # regardless of whether we enqueue again
                if incident.assigned_volunteer_id:
                    blacklist_volunteer_timedout(
                        volunteer_id=incident.assigned_volunteer_id,
                        incident_id=incident.id
                    )
                    print(
                        f"Volunteer {incident.assigned_volunteer_id} "
                        f"timed out on incident {incident.id}"
                    )

                # reset assignment fields
                incident.assigned_volunteer_id = None
                incident.assigned_at = None
                incident.status = "searching"
                db.commit()

                # only enqueue if not already running
                if is_incident_enqueued(incident.id):
                    continue
                mark_incident_enqueued(incident.id)
                assignment_queue.enqueue(
                    assign_volunteer,
                    incident.id,
                    job_timeout=120
                )
                print(f"Enqueued reassignment for incident {incident.id}")

        # ── Case 2: searching, retry every 30s ──────────────────────────
        retry_cutoff = now - timedelta(seconds=30)
        searching = db.query(Incident).filter(
            Incident.status == "searching",
            Incident.assignment_attempts <= 5,
            or_(
                Incident.last_attempted_at.is_(None),
                Incident.last_attempted_at < retry_cutoff
            )
        ).all()

        if searching:
            print(f"Timeout worker: {len(searching)} incidents still searching")
            for incident in searching:
                if is_incident_enqueued(incident.id):
                    continue
                mark_incident_enqueued(incident.id)
                assignment_queue.enqueue(
                    assign_volunteer,
                    incident.id,
                    job_timeout=120
                )
                print(f"Retrying assignment for incident {incident.id}")

    except Exception as e:
        print(f"ERROR in timeout worker: {e}")
        import traceback
        traceback.print_exc()
    finally:
        db.close()