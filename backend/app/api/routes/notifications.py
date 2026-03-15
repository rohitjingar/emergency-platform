# app/api/routes/notifications.py
from fastapi import APIRouter, Depends
from sqlalchemy.orm import Session
from app.db.database import get_db
from app.core.dependencies import get_current_user
from app.models.notification import Notification

router = APIRouter(prefix="/notifications", tags=["Notifications"])

@router.get("/my")
def get_my_notifications(
    skip: int = 0,
    limit: int = 20,
    db: Session = Depends(get_db),
    current_user: dict = Depends(get_current_user)
):
    """Get notifications for current user — unread first."""
    user_id = int(current_user["sub"])
    notifications = db.query(Notification).filter(
        Notification.user_id == user_id
    ).order_by(
        Notification.is_read.asc(),   # unread first
        Notification.created_at.desc()
    ).offset(skip).limit(limit).all()

    return {
        "notifications": [
            {
                "id": n.id,
                "type": n.type,
                "message": n.message,
                "incident_id": n.incident_id,
                "is_read": n.is_read,
                "created_at": n.created_at
            }
            for n in notifications
        ],
        "count": len(notifications)
    }

@router.patch("/{notification_id}/read")
def mark_read(
    notification_id: int,
    db: Session = Depends(get_db),
    current_user: dict = Depends(get_current_user)
):
    user_id = int(current_user["sub"])
    notification = db.query(Notification).filter(
        Notification.id == notification_id,
        Notification.user_id == user_id
    ).first()
    if not notification:
        from fastapi import HTTPException
        raise HTTPException(status_code=404, detail="Notification not found.")
    notification.is_read = True
    db.commit()
    return {"message": "Marked as read"}