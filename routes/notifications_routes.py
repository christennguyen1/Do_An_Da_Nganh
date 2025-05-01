# app/routes/notifications.py
from fastapi import APIRouter, Depends, Request
from controller.notification_controller import (
    controller_create_notification, 
    controller_get_notifications, 
    controller_mark_as_seen,
    controller_broadcast_notification
)
from fastapi.security import OAuth2PasswordBearer

router = APIRouter()
oauth2_scheme = OAuth2PasswordBearer(tokenUrl="signin")

@router.post("/create")
async def create_notification(request: Request, token: str = Depends(oauth2_scheme)):
    body = await request.json()
    return await controller_create_notification(body, token)

@router.get("/user/{user_id}")
async def get_notifications(user_id: int, token: str = Depends(oauth2_scheme)):
    return await controller_get_notifications(user_id, token)

@router.patch("/mark_as_seen/{user_id}/{notification_id}")
async def mark_as_seen(user_id: int, notification_id: int, token: str = Depends(oauth2_scheme)):
    return await controller_mark_as_seen(user_id, notification_id, token)

@router.post("/broadcast")
async def broadcast_notification(request: Request, token: str = Depends(oauth2_scheme)):
    body = await request.json()
    return await controller_broadcast_notification(body, token)

@router.get("/test/{user_id}")
async def test_notification(user_id: int, message: str = "Đây là thông báo test", token: str = Depends(oauth2_scheme)):
    """API test gửi thông báo cho người dùng cụ thể"""
    body = {
        "user_id": user_id,
        "message": message
    }
    return await controller_create_notification(body, token)