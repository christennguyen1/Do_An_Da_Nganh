from pydantic import BaseModel
from bson import ObjectId


class SensorData(BaseModel):
    lux: float
    temperature: float
    humidity: float

    class Config:
        # Dùng để hỗ trợ chuyển đổi ObjectId sang string trong Pydantic model
        json_encoders = {
            ObjectId: str
        }

class User(BaseModel):
    username: str
    password: str