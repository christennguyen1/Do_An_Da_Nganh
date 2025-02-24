from fastapi import FastAPI, WebSocket, WebSocketDisconnect
from fastapi.middleware.cors import CORSMiddleware
from routes import user_routes, sensor_routes, relay_routes, setup_routes, notifications_routes
import uvicorn
from middleware.websocket_manager import add_connection, remove_connection  # Import từ module mới
from databases.databases import *
from schemas import Notification


app = FastAPI()

# Enable CORS
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],  # Allows all origins; specify domains for stricter security
    allow_credentials=True,
    allow_methods=["*"],  # Allows all HTTP methods
    allow_headers=["*"],  # Allows all headers
)

active_connections = {}

@app.websocket("/ws/{user_id}")
async def websocket_endpoint(websocket: WebSocket, user_id: int):
    await websocket.accept()
    await add_connection(user_id, websocket)  # Thêm kết nối vào danh sách
    try:
        while True:
            data = await websocket.receive_text()  # Lắng nghe dữ liệu nếu cần
            print(f"Received: {data} from User {user_id}")

            # Lưu vào MongoDB
            notification = Notification(user_id=user_id, message=data)
            collection_notification.insert_one(notification.to_dict())  # MongoDB

    except WebSocketDisconnect:
        await remove_connection(user_id)  # Xóa kết nối khi bị ngắt

# Include routers
app.include_router(user_routes.router, tags=['Users'], prefix='/api/users')
app.include_router(sensor_routes.router, tags=['Sensors'], prefix='/api/sensors')
app.include_router(relay_routes.router, tags=['Relay'], prefix='/api/relay')
app.include_router(setup_routes.router, tags=['Setup'], prefix='/api/setup')
app.include_router(notifications_routes.router, tags=['Notification'], prefix="/api/notifications")

@app.get("/ping")
def ping():
    return {"message": "Server is running"}

if __name__ == "__main__":
    uvicorn.run("main:app", host="0.0.0.0", port=8080, reload=True)