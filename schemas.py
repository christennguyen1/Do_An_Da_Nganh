from pydantic import BaseModel, Field
from bson import ObjectId
from datetime import datetime  # Import datetime để sử dụng
from typing import Dict, Any, Optional

class SensorData(BaseModel):
    lux: float
    temperature: float
    humidity: float
    soil: float
    timestamp: str 

    class Config:
        # Dùng để hỗ trợ chuyển đổi ObjectId sang string trong Pydantic model
        json_encoders = {
            ObjectId: str
        }

class RelayData(BaseModel):
    relayName: str
    email_user: str
    status: str
    timestamp: str 

    class Config:
        # Dùng để hỗ trợ chuyển đổi ObjectId sang string trong Pydantic model
        json_encoders = {
            ObjectId: str
        }

class SensorDataMonth(BaseModel):
    lux: float
    temperature: float
    humidity_soil: float
    N_soil: float
    P_soil: float
    K_soil: float
    month: str  # Thay đổi kiểu dữ liệu thành datetime
    year: int

    class Config:
        # Dùng để hỗ trợ chuyển đổi ObjectId sang string trong Pydantic model
        json_encoders = {
            ObjectId: str
        }

class SchedulerData(BaseModel):
    id: str
    email_user: str
    relayName: str
    timeStart: str  
    timeEnd: str
    timestamps: str

    class Config:
        # Dùng để hỗ trợ chuyển đổi ObjectId sang string trong Pydantic model
        json_encoders = {
            ObjectId: str
        }

class SensorDataWeek(BaseModel):
    lux: float
    temperature: float
    humidity_soil: float
    N_soil: float
    P_soil: float
    K_soil: float
    day: str  # Thay đổi kiểu dữ liệu thành datetime

    class Config:
        # Dùng để hỗ trợ chuyển đổi ObjectId sang string trong Pydantic model
        json_encoders = {
            ObjectId: str
        }

class SensorDataDay(BaseModel):
    lux: float
    temperature: float
    humidity: float
    soil: float
    hour: int  # Thay đổi kiểu dữ liệu thành datetime

    class Config:
        # Dùng để hỗ trợ chuyển đổi ObjectId sang string trong Pydantic model
        json_encoders = {
            ObjectId: str
        }

class User(BaseModel):
    username: str
    password: str

class UserInfo(BaseModel):
    firstName: str
    lastName: str
    username: str
    email: str
    phoneNumber: str
    address: str

class Notification(BaseModel):
    user_id: int
    message: str
    type: str = "info"  # "info", "warning", "alert", "error"
    data: Optional[Dict[str, Any]] = Field(default_factory=dict)
    is_read: bool = False
    created_at: datetime = Field(default_factory=datetime.now)
    
    def to_dict(self) -> Dict[str, Any]:
        return {
            "user_id": self.user_id,
            "message": self.message,
            "type": self.type,
            "data": self.data,
            "is_read": self.is_read,
            "created_at": self.created_at
        }
    
class Notification(BaseModel):
    user_id: int
    message: str
    type: str = "info"  # "info", "warning", "alert", "error"
    data: Optional[Dict[str, Any]] = Field(default_factory=dict)
    is_read: bool = False
    seen: bool = False  # Giữ lại trường seen để tương thích với API mark_as_seen
    created_at: datetime = Field(default_factory=datetime.now)
    
    def to_dict(self) -> Dict[str, Any]:
        return {
            "user_id": self.user_id,
            "message": self.message,
            "type": self.type,
            "data": self.data,
            "is_read": self.is_read,
            "seen": self.seen,
            "created_at": self.created_at
        }
        
    @classmethod
    def from_dict(cls, data: Dict[str, Any]) -> "Notification":
        return cls(
            user_id=data["user_id"],
            message=data["message"],
            type=data.get("type", "info"),
            data=data.get("data", {}),
            is_read=data.get("is_read", False),
            seen=data.get("seen", False),
            created_at=data.get("created_at", datetime.now())
        )