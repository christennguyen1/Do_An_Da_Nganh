# Tạo một file test riêng để kiểm tra hàm send_notification
import asyncio
from middleware.websocket_manager import send_notification

async def test_notification():
    await send_notification(
        user_id=1,
        message="Test notification",
        notification_type="test",
        data={"test": True}
    )

if __name__ == "__main__":
    asyncio.run(test_notification())