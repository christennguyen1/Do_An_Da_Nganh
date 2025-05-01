# app/controller/notification_controller.py
from services.notification_service import create_notification, get_notifications_by_user, mark_as_seen
from fastapi import HTTPException, status
from middleware.websocket_manager import send_notification

async def controller_create_notification(body: dict, token: str):
    user_id = body.get('user_id')
    message = body.get('message')
    notification_type = body.get('type', 'info')
    data = body.get('data', {})
    
    if not user_id or not message:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="Missing user_id or message"
        )
    
    # Tạo thông báo trong database
    notification = await create_notification(user_id, message)
    
    # Gửi thông báo qua WebSocket nếu người dùng đang online
    await send_notification(user_id, message, notification_type, data)
        
    return notification

async def controller_get_notifications(user_id: int, token: str):
    notifications = await get_notifications_by_user(user_id)
    return notifications

async def controller_mark_as_seen(user_id: int, notification_id: int, token: str):
    result = await mark_as_seen(user_id, notification_id)
    if not result:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Notification not found"
        )
    return {"message": "Notification marked as seen"}

async def controller_broadcast_notification(body: dict, token: str):
    message = body.get('message')
    notification_type = body.get('type', 'info')
    data = body.get('data', {})
    
    if not message:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="Missing message"
        )
    
    # Broadcast được xử lý bởi websocket_manager
    from middleware.websocket_manager import broadcast_notification
    result = await broadcast_notification(message, notification_type, data)
    
    return {
        "message": "Notification broadcasted",
        "delivered_to": len(result),
        "results": result
    }