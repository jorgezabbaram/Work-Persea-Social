from fastapi import APIRouter, Request
from pydantic import BaseModel

router = APIRouter()

class NotificationRequest(BaseModel):
    recipient: str
    message: str
    type: str = "email"

@router.get("/health")
async def health_check():
    return {"status": "healthy", "service": "notification-service"}

@router.post("/notifications")
async def send_notification(notification: NotificationRequest):
    return {
        "id": "notif_123",
        "status": "sent",
        "recipient": notification.recipient,
        "type": notification.type
    }

@router.get("/notifications")
async def get_notifications(request: Request):
    service = request.app.state.notification_service
    return {"notifications": service.get_notifications()}