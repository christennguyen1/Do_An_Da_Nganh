# backend/utils/websocket_manager.py


from fastapi import WebSocket, WebSocketDisconnect
from typing import List






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


async def remove_connection(user_id: int):
    if user_id in active_connections:
        del active_connections[user_id]


async def send_notification(user_id: int, message: str):
    if user_id in active_connections:
        websocket = active_connections[user_id]
        await websocket.send_text(message)









