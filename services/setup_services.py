from databases.databases import *
from datetime import datetime
from constant.constant import nutnhan
import json
import pytz
from bson import ObjectId


def service_setup_temperature(body):
    data = body

    email_user = data.get('email_user')
    temperature_value = data.get('temperature_value')
    status = data.get('status')

    if collection_user.count_documents({"email": email_user}) == 0:
        return {
            'message': 'User was not registed',
            'data': []
        }, 200
    
    vietnam_tz = pytz.timezone('Asia/Ho_Chi_Minh')
    vietnam_time = datetime.now(vietnam_tz)

    data = {
        'email_user': email_user,
        'value': temperature_value,
        'status': status,
        'timestamp': vietnam_time,
    }

    collection_setup_temperature.insert_one(data)
    
    publish_to_adafruit("va-tem", temperature_value if status == "ON" else 0)
        

    return {
        'message': 'Create Relay successful',
        'data': {
            'email_user': email_user,
            'value': temperature_value,
            'status': status,
            'timestamp': vietnam_time,
        }
    }, 200


def service_setup_pir(body):
    data = body

    email_user = data.get('email_user')
    pir_value = data.get('pir_value')
    status = data.get('status')

    if collection_user.count_documents({"email": email_user}) == 0:
        return {
            'message': 'User was not registed',
            'data': []
        }, 200
    
    vietnam_tz = pytz.timezone('Asia/Ho_Chi_Minh')
    vietnam_time = datetime.now(vietnam_tz)

    data = {
        'email_user': email_user,
        'value': pir_value,
        'status': status,
        'timestamp': vietnam_time,
    }

    collection_setup_pir.insert_one(data)

    publish_to_adafruit("va-pir", pir_value if status == "ON" else 0)
        
    return {
        'message': 'Create Relay successful',
        'data': {
            'email_user': email_user,
            'value': pir_value,
            'status': status,
            'timestamp': vietnam_time,
        }
    }, 200



def service_setup_light(body):
    data = body

    email_user = data.get('email_user')
    light_value = data.get('light_value')
    status = data.get('status')

    if collection_user.count_documents({"email": email_user}) == 0:
        return {
            'message': 'User was not registed',
            'data': []
        }, 200
    
    vietnam_tz = pytz.timezone('Asia/Ho_Chi_Minh')
    vietnam_time = datetime.now(vietnam_tz)

    data = {
        'email_user': email_user,
        'value': light_value,
        'status': status,
        'timestamp': vietnam_time,
    }

    collection_setup_light.insert_one(data)

    publish_to_adafruit("va-lux", light_value if status == "ON" else 0)
        
    return {
        'message': 'Create Set up light successful',
        'data': {
            'email_user': email_user,
            'value': light_value,
            'status': status,
            'timestamp': vietnam_time,
        }
    }, 200


def service_create_setup_scheduler(body):
    data = body

    print("Hello3: ",data)

    email_user = data.get('email')
    relayName = data.get('relayName')
    timeStart = data.get('timeStart')
    timeEnd = data.get('timeEnd')

    if collection_user.count_documents({"email": email_user}) == 0:
        return {
            'message': 'User was not registed',
            'data': []
        }, 200
    
    vietnam_tz = pytz.timezone('Asia/Ho_Chi_Minh')
    vietnam_time = datetime.now(vietnam_tz)

    data = {
        'email_user': email_user,
        'relayName': relayName,
        'timeStart': timeStart,
        'timeEnd': timeEnd,
        'timestamp': vietnam_time,
    }

    collection_setup_scheduler.insert_one(data)

    print(data)
        
    return {
        'message': 'Create scheduler successful',
        'data': {
            'email_user': email_user,
            'relayName': relayName,
            'timeStart': timeStart,
            'timeEnd': timeEnd,
            'timestamp': vietnam_time
        }
    }, 200


def service_get_setup_scheduler():
    # Lấy tất cả dữ liệu từ MongoDB
    schedulerList = list(collection_setup_scheduler.find())  # ✅ Convert Cursor thành list

    # Kiểm tra nếu không có dữ liệu
    if not schedulerList:  
        return {
            'message': 'No scheduler found in system', 
            'errCode': 1
        }, 400
    
    # Chuyển đổi dữ liệu thành danh sách dictionary
    scheduler_data_list = [
        {
            "id": str(scheduler["_id"]),  # ✅ Chuyển ObjectId thành string
            "relayName": scheduler["relayName"],
            "timeStart": scheduler["timeStart"],
            "timeEnd": scheduler["timeEnd"],
            "timestamp": scheduler["timestamp"].strftime("%Y-%m-%dT%H:%M:%S") 
                if isinstance(scheduler["timestamp"], datetime) else scheduler["timestamp"],
        }
        for scheduler in schedulerList
    ]

    print(scheduler_data_list)

    return {
        'message': 'Get Scheduler successful',
        'data': scheduler_data_list
    }, 200

def service_get_setup_scheduler_ByID(body):
    # Lấy tất cả dữ liệu từ MongoDB
    data = body

    id = data.get('id')

    object_id = ObjectId(id)

    scheduler = collection_setup_scheduler.find_one({'_id': object_id})  # ✅ Convert Cursor thành list

    # Kiểm tra nếu không có dữ liệu
    if not scheduler:  
        return {
            'message': 'No scheduler found in system', 
            'errCode': 1
        }, 400
    
    print(scheduler)

    return {
        'message': 'Get scheduler By ID successful',
        'data': {
            'email_user': scheduler["email_user"],
            'relayName': scheduler["relayName"],
            'timeStart': scheduler["timeStart"],
            'timeEnd': scheduler["timeEnd"],
            'timestamp': scheduler["timestamp"].strftime("%Y-%m-%dT%H:%M:%S") 
                if isinstance(scheduler["timestamp"], datetime) else scheduler["timestamp"]
        }
    }, 200


def service_update_setup_scheduler(body):
    # Lấy tất cả dữ liệu từ MongoDB
    if not body.get('id') or not body.get('email'):
        return {
            'message': 'Email or ID_Device is required', 
            'errCode': 1
        }, 400

    id = body.get('id')
    email = body.get('email')
    timeStart = body.get('timeStart')
    timeEnd = body.get('timeEnd')

    # Chuyển đổi ID sang ObjectId
    object_id = ObjectId(id)

    # Kiểm tra xem scheduler có tồn tại không
    scheduler = collection_setup_scheduler.find_one({'_id': object_id})
    if not scheduler:
        return {
            'message': 'Device not found', 
            'errCode': 1
        }, 404

    # Kiểm tra xem user có tồn tại không
    user = collection_user.find_one({'email': email})
    if not user:
        return {
            'message': 'User not found', 
            'errCode': 1
        }, 404

    # Tạo danh sách giá trị cần update
    new_values = {"$set": {}}

    if email:
        new_values["$set"]['email_user'] = email

    if timeStart:
        new_values["$set"]['timeStart'] = timeStart

    if timeEnd:
        new_values["$set"]['timeEnd'] = timeEnd

    # Thực hiện update
    collection_setup_scheduler.update_one({"_id": object_id}, new_values)

    # Lấy dữ liệu sau khi update để trả về
    updated_scheduler = collection_setup_scheduler.find_one({"_id": object_id})

    return {
        'message': 'Update scheduler successful',
        'data': {
                'email_user': updated_scheduler.get('email_user'),
                'relayName': updated_scheduler.get("relayName"),
                'timeStart': updated_scheduler.get("timeStart"),
                'timeEnd': updated_scheduler.get("timeEnd"),
                'timestamp': updated_scheduler["timestamp"].strftime("%Y-%m-%dT%H:%M:%S") 
                    if isinstance(updated_scheduler["timestamp"], datetime) else updated_scheduler["timestamp"]
            }
        }, 200



def service_delete_setup_scheduler(body):
    data = body
    
    if not body.get("id"):
         return {
            "message": "ID is required",
            "errCode": 1
        }, 400
    
    id = data.get("id")

    # Chuyển đổi ID từ string -> ObjectId
    object_id = ObjectId(id)

    # Tìm dữ liệu trước khi xóa
    scheduler = collection_setup_scheduler.find_one({"_id": object_id})
    if not scheduler:
        return {
            "message": "No scheduler found in system",
            "errCode": 1
        }, 400

    # Xóa bản ghi theo ID
    collection_setup_scheduler.delete_one({"_id": object_id})

    return {
        "message": "Scheduler deleted successfully",
        "data": {
            "id": str(object_id),
            "timestamp": datetime.now().strftime("%Y-%m-%dT%H:%M:%S")
        }
    }, 200