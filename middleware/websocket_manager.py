# backend/utils/websocket_manager.py

from fastapi import WebSocket

# Dictionary lưu trữ kết nối WebSocket
active_connections = {}

async def add_connection(user_id: int, websocket: WebSocket):
    active_connections[user_id] = websocket

async def remove_connection(user_id: int):
    if user_id in active_connections:
        del active_connections[user_id]

async def send_notification(user_id: int, message: str):
    if user_id in active_connections:
        websocket = active_connections[user_id]
        await websocket.send_text(message)
