from pydantic import BaseModel
from bson import ObjectId
from datetime import datetime  # Import datetime để sử dụng

class SensorData(BaseModel):
    lux: float
    temperature: float
    humidity: float
    timestamp: str  # Thay đổi kiểu dữ liệu thành datetime

    class Config:
        # Dùng để hỗ trợ chuyển đổi ObjectId sang string trong Pydantic model
        json_encoders = {
            ObjectId: str
        }

class User(BaseModel):
    username: str
    password: str

class Notification:
    def __init__(self, user_id, message, timestamp=None, seen=False):
        self.user_id = user_id
        self.message = message
        self.timestamp = timestamp if timestamp else datetime.utcnow()
        self.seen = seen

    def to_dict(self):
        return {
            'user_id': self.user_id,
            'message': self.message,
            'timestamp': self.timestamp,
            'seen': self.seen
        }