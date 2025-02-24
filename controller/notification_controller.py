# app/controller/notification_controller.py

from services.notification_service import create_notification
from fastapi import HTTPException, status
from middleware.websocket_manager import send_notification  # Import từ websocket_manager.py


async def controller_create_notification(body: dict, token: str):
    user_id = body.get('user_id')
    message = body.get('message')

    if not user_id or not message:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="Missing user_id or message"
        )

    notification = await create_notification(user_id, message)

    # Gửi thông báo qua WebSocket nếu người dùng đang online
    await send_notification(user_id, message)
    
    return notification

async def controller_get_notifications(user_id: int, token: str):
    notifications = await notification_service.get_notifications_by_user(user_id)
    return notifications

async def controller_mark_as_seen(user_id: int, notification_id: int, token: str):
    result = await notification_service.mark_as_seen(user_id, notification_id)
    if not result:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Notification not found"
        )
    return {"message": "Notification marked as seen"}
