# app/service/notification_service.py

from schemas import Notification
from databases.databases import *

async def create_notification(self, user_id: int, message: str):
    notification = Notification(user_id=user_id, message=message)
    await collection_notification.insert_one(notification.to_dict())  # MongoDB
    return notification.to_dict()

async def get_notifications_by_user(self, user_id: int):
    notifications = await collection_notification.find({'user_id': user_id}).to_list(length=100)
    return [notification for notification in notifications]

async def mark_as_seen(self, user_id: int, notification_id: int):
    result = await collection_notification.update_one(
        {'user_id': user_id, '_id': notification_id},
        {'$set': {'seen': True}}
    )
    return result.modified_count > 0
