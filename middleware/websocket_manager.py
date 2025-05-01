# backend/utils/websocket_manager.py
from fastapi import WebSocket, WebSocketDisconnect
from typing import List, Dict, Any, Optional

# Dictionary lưu trữ kết nối WebSocket
active_connections = {}

# Danh sách kết nối WebSocket cho relay
relay_connections: List[WebSocket] = []

async def websocket_relay_endpoint(websocket: WebSocket):
    print("Attempting WebSocket connection to /ws/relay")
    await websocket.accept()
    print("WebSocket connection accepted")
    relay_connections.append(websocket)
    try:
        while True:
            await websocket.receive_text()  # Giữ kết nối mở
    except WebSocketDisconnect:
        relay_connections.remove(websocket)
        print("Relay WebSocket disconnected")
    except Exception as e:
        print(f"WebSocket error: {e}")

async def broadcast_relay_update(relay_data: dict):
    print(f"Broadcasting relay data: {relay_data}")
    for connection in relay_connections:
        try:
            await connection.send_json(relay_data)
        except Exception as e:
            print(f"Error broadcasting to relay client: {e}")

async def add_connection(user_id: int, websocket: WebSocket):
    active_connections[user_id] = websocket
    print(f"User {user_id} connected. Total connections: {len(active_connections)}")

async def remove_connection(user_id: int):
    if user_id in active_connections:
        del active_connections[user_id]
        print(f"User {user_id} disconnected. Total connections: {len(active_connections)}")

async def send_notification(user_id: int, message: str, notification_type: str = "info", data: Optional[Dict[str, Any]] = None):
    """
    Gửi thông báo đến người dùng cụ thể
    
    Args:
        user_id: ID người dùng nhận thông báo
        message: Nội dung thông báo
        notification_type: Loại thông báo (info, warning, alert, error)
        data: Dữ liệu bổ sung kèm theo thông báo
    """
    # Gửi notification nếu user đang online
    if user_id in active_connections:
        try:
            websocket = active_connections[user_id]
            
            # Format thông báo dưới dạng JSON
            notification_data = {
                "type": "notification",
                "notification_type": notification_type,
                "message": message
            }
            
            # Thêm data nếu có
            if data:
                notification_data["data"] = data
                
            await websocket.send_json(notification_data)
            return True
        except Exception as e:
            print(f"Error sending notification to user {user_id}: {str(e)}")
    
    return False

async def broadcast_notification(message: str, notification_type: str = "info", data: Optional[Dict[str, Any]] = None):
    """
    Gửi thông báo đến tất cả người dùng đang kết nối
    
    Args:
        message: Nội dung thông báo
        notification_type: Loại thông báo
        data: Dữ liệu bổ sung kèm theo thông báo
    """
    results = {}
    
    # Format thông báo dưới dạng JSON
    notification_data = {
        "type": "notification",
        "notification_type": notification_type,
        "message": message
    }
    
    # Thêm data nếu có
    if data:
        notification_data["data"] = data
    
    # Gửi đến tất cả user đang online
    for user_id, websocket in active_connections.items():
        try:
            await websocket.send_json(notification_data)
            results[user_id] = True
        except Exception as e:
            print(f"Error broadcasting to user {user_id}: {str(e)}")
            results[user_id] = False
    
    return results