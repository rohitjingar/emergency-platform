from sqlalchemy.orm import Session
from app.models.notification import Notification

# notification types
VOLUNTEER_INCIDENT_ASSIGNED = "volunteer_incident_assigned"
VOLUNTEER_PLEASE_GO_OFFLINE = "volunteer_please_go_offline"
AFFECTED_VOLUNTEER_ASSIGNED = "affected_volunteer_assigned"
AFFECTED_NO_VOLUNTEER = "affected_no_volunteer"
ADMIN_NO_VOLUNTEER_FOUND = "admin_no_volunteer_found"

def create_notification(
    db: Session,
    user_id: int,
    notification_type: str,
    message: str,
    incident_id: int | None = None
) -> Notification:
    notification = Notification(
        user_id=user_id,
        incident_id=incident_id,
        type=notification_type,
        message=message,
        is_read=False
    )
    db.add(notification)
    db.commit()
    db.refresh(notification)
    return notification

def notify_volunteer_assigned(
    db: Session,
    volunteer_user_id: int,
    incident_id: int,
    incident_type: str,
    severity: str,
    distance_km: float
) -> None:
    create_notification(
        db=db,
        user_id=volunteer_user_id,
        notification_type=VOLUNTEER_INCIDENT_ASSIGNED,
        message=(
            f"Emergency nearby: {incident_type.upper()} incident "
            f"({severity}) — {distance_km}km from your location. "
            f"Please accept or decline within 60 seconds."
        ),
        incident_id=incident_id
    )

def notify_volunteer_please_go_offline(
    db: Session,
    volunteer_user_id: int
) -> None:
    create_notification(
        db=db,
        user_id=volunteer_user_id,
        notification_type=VOLUNTEER_PLEASE_GO_OFFLINE,
        message=(
            "You declined an incident with no time window. "
            "Your status has been set to offline. "
            "Please update your status to available when you are ready."
        )
    )

def notify_affected_user_assigned(
    db: Session,
    affected_user_id: int,
    incident_id: int,
    volunteer_user_id: int,
    distance_km: float
) -> None:
    create_notification(
        db=db,
        user_id=affected_user_id,
        notification_type=AFFECTED_VOLUNTEER_ASSIGNED,
        message=(
            f"Help is on the way. A verified volunteer "
            f"{distance_km}km away has accepted your emergency request."
        ),
        incident_id=incident_id
    )

def notify_affected_no_volunteer(
    db: Session,
    affected_user_id: int,
    incident_id: int
) -> None:
    create_notification(
        db=db,
        user_id=affected_user_id,
        notification_type=AFFECTED_NO_VOLUNTEER,
        message=(
            "We could not find an available volunteer for your emergency. "
            "Please call 112 immediately. Our team has been alerted."
        ),
        incident_id=incident_id
    )

def notify_admin_no_volunteer(
    db: Session,
    incident_id: int,
    incident_type: str,
    severity: str
) -> None:
    # get all admin user ids
    from app.models.user import User
    admins = db.query(User).filter(User.role == "admin").all()
    for admin in admins:
        create_notification(
            db=db,
            user_id=admin.id,
            notification_type=ADMIN_NO_VOLUNTEER_FOUND,
            message=(
                f"ALERT: No volunteer found for incident #{incident_id} "
                f"({incident_type.upper()}, {severity}) after 5 attempts. "
                f"Manual intervention required."
            ),
            incident_id=incident_id
        )