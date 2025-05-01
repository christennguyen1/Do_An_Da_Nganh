# app/service/notification_service.py
from schemas import Notification
from databases.databases import collection_notification

async def create_notification(user_id: int, message: str):
    """
    Tạo thông báo mới
    
    Args:
        user_id: ID của người dùng nhận thông báo
        message: Nội dung thông báo
    """
    notification = Notification(user_id=user_id, message=message)
    result = collection_notification.insert_one(notification.to_dict())  # MongoDB
    
    # Chuyển ObjectId thành string để có thể serialize
    notification_dict = notification.to_dict()
    notification_dict["_id"] = str(result.inserted_id)
    
    return notification_dict

async def get_notifications_by_user(user_id: int):
    """
    Lấy danh sách thông báo của người dùng
    
    Args:
        user_id: ID của người dùng
    """
    notifications = collection_notification.find({'user_id': user_id}).sort("created_at", -1).to_list(length=100)
    
    # Chuyển ObjectId thành string để có thể serialize
    for notification in notifications:
        if "_id" in notification:
            notification["_id"] = str(notification["_id"])
    
    return notifications

async def mark_as_seen(user_id: int, notification_id: int):
    """
    Đánh dấu thông báo đã được xem
    
    Args:
        user_id: ID của người dùng
        notification_id: ID của thông báo
    """
    result = collection_notification.update_one(
        {'user_id': user_id, '_id': notification_id},
        {'$set': {'seen': True}}
    )
    return result.modified_count > 0