from databases.databases import *
from datetime import datetime
from constant.constant import nutnhan
import json
import pytz
import time
from bson import ObjectId

import requests
import time

def service_get_setup_threshold():
    # Lấy bản ghi đầu tiên từ collection
    existing_threshold = collection_setup_threshold.find_one()

    # Khởi tạo các giá trị mặc định
    temperature_threshold = None
    humidity_threshold = None
    humidity_soil_threshold = None
    light_threshold = None
    object_id = None

    if len(existing_threshold) == 0:
        return {
                'message': 'Threshold not found', 
                'errCode': 1
            }, 404
        
    temperature_threshold = existing_threshold.get('temperature_threshold')
    humidity_threshold = existing_threshold.get('humidity_threshold')
    humidity_soil_threshold = existing_threshold.get('humidity_soil_threshold')
    light_threshold = existing_threshold.get('light_threshold')

    return {
        'message': 'Create threshold successful',
        'data': {
            "temperature_threshold": temperature_threshold,
            "humidity_threshold": humidity_threshold,
            "humidity_soil_threshold": humidity_soil_threshold,
            "light_threshold": light_threshold
        }
    }, 200

def service_put_setup_threshold(body):
    data = body
    
    temperature = data.get('temperature_threshold')
    humidity = data.get('humidity_threshold')
    humidity_soil = data.get('humidity_soil_threshold')
    light = data.get('light_threshold')
    
    # Lấy bản ghi đầu tiên từ collection
    existing_threshold = collection_setup_threshold.find_one()

    # Khởi tạo các giá trị mặc định
    temperature_threshold = None
    humidity_threshold = None
    humidity_soil_threshold = None
    light_threshold = None
    object_id = None

    if existing_threshold:
        object_id = existing_threshold.get('_id')
        temperature_threshold = existing_threshold.get('temperature_threshold')
        humidity_threshold = existing_threshold.get('humidity_threshold')
        humidity_soil_threshold = existing_threshold.get('humidity_soil_threshold')
        light_threshold = existing_threshold.get('light_threshold')

    value = None

    if existing_threshold:
        value = collection_setup_scheduler.insert_one(data)

    new_values = {"$set": {}}

    if temperature:
        new_values["$set"]['temperature_threshold'] = temperature
    else:
        new_values["$set"]['temperature_threshold'] = temperature_threshold

    if humidity:
        new_values["$set"]['humidity_threshold'] = humidity
    else:
        new_values["$set"]['humidity_threshold'] = humidity_threshold

    if humidity_soil:
        new_values["$set"]['humidity_soil_threshold'] = humidity_soil
    else:
        new_values["$set"]['humidity_soil_threshold'] = humidity_soil_threshold

    if light:
        new_values["$set"]['light_threshold'] = light
    else:
        new_values["$set"]['light_threshold'] = light_threshold

    # Thực hiện update
    if object_id:
        collection_setup_scheduler.update_one({"_id": object_id}, new_values)
    else:
        # Cập nhật hoặc chèn mới vào collection_setup_threshold
        value = collection_setup_threshold.update_one(
            {"_id": object_id} if object_id else {},
            new_values,
            upsert=True
        )

    # Tạm thời bỏ các biến không xác định trong value_data
    value_data = f'0_{str(object_id or "new")}'  # Không thể dùng relayName, timeStart, timeEnd, repeatDaily
    print(value_data)

    core_iot_url = "https://app.coreiot.io/api/plugins/telemetry/DEVICE/21c4e8a0-f63f-11ef-a887-6d1a184f2bb5/SHARED_SCOPE"
    core_iot_body = {
        "temperature_threshold": new_values["$set"]['temperature_threshold'],
        "humidity_threshold": new_values["$set"]['humidity_threshold'],
        "humidity_soil_threshold": new_values["$set"]['humidity_soil_threshold'],
        "light_threshold": new_values["$set"]['light_threshold']
    }
   
    token = "eyJhbGciOiJIUzUxMiJ9.eyJzdWIiOiJ2aW5oLm5ndXllbjEyM0BoY211dC5lZHUudm4iLCJ1c2VySWQiOiJjOWY5OGNmMC1lMTQ2LTExZWYtYWQwOS01MTVmNzkwZWQ5ZGYiLCJzY29wZXMiOlsiVEVOQU5UX0FETUlOIl0sInNlc3Npb25JZCI6ImU4MzU5YzgxLWQ2NmEtNDljYi05NjgyLWE3MTg0MDFlOTQ4YyIsImV4cCI6MTc0MjAyMDQzMSwiaXNzIjoiY29yZWlvdC5pbyIsImlhdCI6MTc0MjAxMTQzMSwiZmlyc3ROYW1lIjoiVklOSCIsImxhc3ROYW1lIjoiTkdVWeG7hE4gS0jhuq5DIiwiZW5hYmxlZCI6dHJ1ZSwiaXNQdWJsaWMiOmZhbHNlLCJ0ZW5hbnRJZCI6ImM5ZTk4NzYwLWUxNDYtMTFlZi1hZDA5LTUxNWY3OTBlZDlkZiIsImN1c3RvbWVySWQiOiIxMzgxNDAwMC0xZGQyLTExYjItODA4MC04MDgwODA4MDgwODAifQ.mS-l5RJ-zRfHzJ237nGnnBNidf2KsQqnb0mgJWJtw8voOdkpMlOH3wuQvUtaKIV9qn8BZhr60E_DRrCzaDvp7w"
    headers = {
        "Content-Type": "application/json",
        "X-Authorization": f"Bearer {token}"
    }
   
    max_retries = 2
    for attempt in range(max_retries):
        try:
            response = requests.post(core_iot_url, headers=headers, json=core_iot_body)
            if response.status_code == 401 and "Token has expired" in response.text:
                login_url = "https://app.coreiot.io/api/auth/login"
                login_body = {"username": "vinh.nguyen123@hcmut.edu.vn", "password": "Vinhnguyen1$"}
                login_response = requests.post(login_url, json=login_body)
                if login_response.status_code == 200:
                    token = login_response.json().get('token')
                    headers["X-Authorization"] = f"Bearer {token}"
                    continue
            if response.status_code == 200:
                print(f"Successfully sent command to Core IOT: {response.text}")
                break
            else:
                print(f"Error sending command to Core IOT: {response.status_code}, {response.text}")
        except Exception as e:
            print(f"Exception when calling Core IOT API: {str(e)}")
        if attempt < max_retries - 1:
            time.sleep(1)
    
    print(value_data)
    
    return {
        'message': 'Create threshold successful',
        'data': {
            "temperature_threshold": new_values["$set"]['temperature_threshold'],
            "humidity_threshold": new_values["$set"]['humidity_threshold'],
            "humidity_soil_threshold": new_values["$set"]['humidity_soil_threshold'],
            "light_threshold": new_values["$set"]['light_threshold']
        }
    }, 200

def service_delete_setup_threshold():
    # Lấy bản ghi đầu tiên từ collection
    existing_threshold = collection_setup_threshold.find_one()

    if len(existing_threshold) == 0:
        return {
                'message': 'Threshold not found', 
                'errCode': 1
            }, 404
    object_id = existing_threshold.get('_id')
    new_values = {"$set": {}}
    new_values["$set"]['temperature_threshold'] = 0
    new_values["$set"]['humidity_threshold'] = 0
    new_values["$set"]['humidity_soil_threshold'] = 0
    new_values["$set"]['light_threshold'] = 0

    print


    # Thực hiện update
    collection_setup_threshold.update_one({"_id": object_id}, new_values)
    

    core_iot_url = "https://app.coreiot.io/api/plugins/telemetry/DEVICE/21c4e8a0-f63f-11ef-a887-6d1a184f2bb5/SHARED_SCOPE"
    core_iot_body = {
        "temperature_threshold": 0,
        "humidity_threshold": 0,
        "humidity_soil_threshold": 0,
        "light_threshold": 0
    }
   
    token = "eyJhbGciOiJIUzUxMiJ9.eyJzdWIiOiJ2aW5oLm5ndXllbjEyM0BoY211dC5lZHUudm4iLCJ1c2VySWQiOiJjOWY5OGNmMC1lMTQ2LTExZWYtYWQwOS01MTVmNzkwZWQ5ZGYiLCJzY29wZXMiOlsiVEVOQU5UX0FETUlOIl0sInNlc3Npb25JZCI6ImU4MzU5YzgxLWQ2NmEtNDljYi05NjgyLWE3MTg0MDFlOTQ4YyIsImV4cCI6MTc0MjAyMDQzMSwiaXNzIjoiY29yZWlvdC5pbyIsImlhdCI6MTc0MjAxMTQzMSwiZmlyc3ROYW1lIjoiVklOSCIsImxhc3ROYW1lIjoiTkdVWeG7hE4gS0jhuq5DIiwiZW5hYmxlZCI6dHJ1ZSwiaXNQdWJsaWMiOmZhbHNlLCJ0ZW5hbnRJZCI6ImM5ZTk4NzYwLWUxNDYtMTFlZi1hZDA5LTUxNWY3OTBlZDlkZiIsImN1c3RvbWVySWQiOiIxMzgxNDAwMC0xZGQyLTExYjItODA4MC04MDgwODA4MDgwODAifQ.mS-l5RJ-zRfHzJ237nGnnBNidf2KsQqnb0mgJWJtw8voOdkpMlOH3wuQvUtaKIV9qn8BZhr60E_DRrCzaDvp7w"
    headers = {
        "Content-Type": "application/json",
        "X-Authorization": f"Bearer {token}"
    }
   
    max_retries = 2
    for attempt in range(max_retries):
        try:
            response = requests.post(core_iot_url, headers=headers, json=core_iot_body)
            if response.status_code == 401 and "Token has expired" in response.text:
                login_url = "https://app.coreiot.io/api/auth/login"
                login_body = {"username": "vinh.nguyen123@hcmut.edu.vn", "password": "Vinhnguyen1$"}
                login_response = requests.post(login_url, json=login_body)
                if login_response.status_code == 200:
                    token = login_response.json().get('token')
                    headers["X-Authorization"] = f"Bearer {token}"
                    continue
            if response.status_code == 200:
                print(f"Successfully sent command to Core IOT: {response.text}")
                break
            else:
                print(f"Error sending command to Core IOT: {response.status_code}, {response.text}")
        except Exception as e:
            print(f"Exception when calling Core IOT API: {str(e)}")
        if attempt < max_retries - 1:
            time.sleep(1)

    
    return {
        'message': 'Delete threshold successful',
        'data': {}
    }, 200




def service_create_setup_scheduler(body):
    data = body
    
    email_user = data.get('email')
    relayName = data.get('relayName')
    timeStart = data.get('timeStart')
    timeEnd = data.get('timeEnd')
    repeatDaily = data.get('repeatDaily')
    
    if collection_user.count_documents({"email": email_user}) == 0:
        return {
            'message': 'User was not registed',
            'data': []
        }, 200
    
    # Convert timeStart and timeEnd to datetime objects for comparison
    # Assuming timeStart and timeEnd are in ISO format "YYYY-MM-DD HH:MM:SS" or similar
    try:
        # Parsing datetime strings - adjust format as needed
        start_datetime = datetime.fromisoformat(timeStart)
        end_datetime = datetime.fromisoformat(timeEnd)
    except ValueError:
        return {
            'message': 'Invalid datetime format. Please use YYYY-MM-DD HH:MM:SS format',
            'data': []
        }, 400
    
    # Check for conflicts with existing schedules for the same relay
    existing_schedules = collection_setup_scheduler.find({
        'relayName': relayName
    })

    if existing_schedules:
        for schedule in existing_schedules:
            # Parse existing datetime strings
            existing_start = datetime.fromisoformat(schedule['timeStart'])
            existing_end = datetime.fromisoformat(schedule['timeEnd'])
            
            # Check for overlap - if new start is before existing end AND new end is after existing start
            if (start_datetime <= existing_start and end_datetime >= existing_end):
                # Format recommendation datetime
                recommended_start = existing_end.strftime("%Y-%m-%d %H:%M:%S")
                
                return {
                    'message': 'Time conflict detected',
                    'data': {
                        'conflict': True,
                        'conflicting_schedule': {
                            'timeStart': schedule['timeStart'],
                            'timeEnd': schedule['timeEnd']
                        },
                        'recommendation': f'You should schedule from {start_datetime.strftime("%Y-%m-%d %H:%M:%S")} to {existing_start.strftime("%Y-%m-%d %H:%M:%S")} and from {existing_end.strftime("%Y-%m-%d %H:%M:%S")} to {end_datetime.strftime("%Y-%m-%d %H:%M:%S")}'
                    }
                }, 409

        
            if (start_datetime >= existing_start and end_datetime <= existing_end):
                # Format recommendation datetime
                recommended_start = existing_end.strftime("%Y-%m-%d %H:%M:%S")
                
                return {
                    'message': 'Time conflict detected',
                    'data': {
                        'conflict': True,
                        'conflicting_schedule': {
                            'timeStart': schedule['timeStart'],
                            'timeEnd': schedule['timeEnd']
                        },
                        'recommendation': f'Scheduler have setted up from {existing_start.strftime("%Y-%m-%d %H:%M:%S")} to {existing_end.strftime("%Y-%m-%d %H:%M:%S")}'
                    }
                }, 409
            
            
            if (start_datetime >= existing_start and end_datetime >= existing_end):
                # Format recommendation datetime
                recommended_start = existing_end.strftime("%Y-%m-%d %H:%M:%S")
                
                return {
                    'message': 'Time conflict detected',
                    'data': {
                        'conflict': True,
                        'conflicting_schedule': {
                            'timeStart': schedule['timeStart'],
                            'timeEnd': schedule['timeEnd']
                        },
                        'recommendation': f'You should schedule from {existing_end.strftime("%Y-%m-%d %H:%M:%S")} to {end_datetime.strftime("%Y-%m-%d %H:%M:%S")}'
                    }
                }, 409
            
            if (start_datetime <= existing_start and end_datetime <= existing_end):
                # Format recommendation datetime
                recommended_start = existing_end.strftime("%Y-%m-%d %H:%M:%S")
                
                return {
                    'message': 'Time conflict detected',
                    'data': {
                        'conflict': True,
                        'conflicting_schedule': {
                            'timeStart': schedule['timeStart'],
                            'timeEnd': schedule['timeEnd']
                        },
                        'recommendation': f'You should schedule from {start_datetime.strftime("%Y-%m-%d %H:%M:%S")} to {existing_start.strftime("%Y-%m-%d %H:%M:%S")}'
                    }
                }, 409
    
    vietnam_tz = pytz.timezone('Asia/Ho_Chi_Minh')
    vietnam_time = datetime.now(vietnam_tz)

    print("Time vietnam: ",vietnam_time)
    
    data = {
        'email': email_user,
        'relayName': relayName,
        'timeStart': timeStart,
        'timeEnd': timeEnd,
        'timestamp': vietnam_time,
        'repeatDaily' : repeatDaily
    }
    
    value = collection_setup_scheduler.insert_one(data)

    value_data = f'{0}_{str(value.inserted_id)}_{relayName}_{timeStart}_{timeEnd}_{int(repeatDaily)}'
    print(value_data)
    core_iot_url = "https://app.coreiot.io/api/plugins/telemetry/DEVICE/21c4e8a0-f63f-11ef-a887-6d1a184f2bb5/SHARED_SCOPE"
    core_iot_body = {
        "scheduler": value_data
    }
   
    token = "eyJhbGciOiJIUzUxMiJ9.eyJzdWIiOiJ2aW5oLm5ndXllbjEyM0BoY211dC5lZHUudm4iLCJ1c2VySWQiOiJjOWY5OGNmMC1lMTQ2LTExZWYtYWQwOS01MTVmNzkwZWQ5ZGYiLCJzY29wZXMiOlsiVEVOQU5UX0FETUlOIl0sInNlc3Npb25JZCI6ImU4MzU5YzgxLWQ2NmEtNDljYi05NjgyLWE3MTg0MDFlOTQ4YyIsImV4cCI6MTc0MjAyMDQzMSwiaXNzIjoiY29yZWlvdC5pbyIsImlhdCI6MTc0MjAxMTQzMSwiZmlyc3ROYW1lIjoiVklOSCIsImxhc3ROYW1lIjoiTkdVWeG7hE4gS0jhuq5DIiwiZW5hYmxlZCI6dHJ1ZSwiaXNQdWJsaWMiOmZhbHNlLCJ0ZW5hbnRJZCI6ImM5ZTk4NzYwLWUxNDYtMTFlZi1hZDA5LTUxNWY3OTBlZDlkZiIsImN1c3RvbWVySWQiOiIxMzgxNDAwMC0xZGQyLTExYjItODA4MC04MDgwODA4MDgwODAifQ.mS-l5RJ-zRfHzJ237nGnnBNidf2KsQqnb0mgJWJtw8voOdkpMlOH3wuQvUtaKIV9qn8BZhr60E_DRrCzaDvp7w"
    headers = {
        "Content-Type": "application/json",
        "X-Authorization": f"Bearer {token}"
    }
   
    max_retries = 2
    for attempt in range(max_retries):
        try:
            response = requests.post(core_iot_url, headers=headers, json=core_iot_body)
            if response.status_code == 401 and "Token has expired" in response.text:
                login_url = "https://app.coreiot.io/api/auth/login"
                login_body = {"username": "vinh.nguyen123@hcmut.edu.vn", "password": "Vinhnguyen1$"}
                login_response = requests.post(login_url, json=login_body)
                if login_response.status_code == 200:
                    token = login_response.json().get('token')
                    headers["X-Authorization"] = f"Bearer {token}"
                    continue
            if response.status_code == 200:
                print(f"Successfully sent command to Core IOT: {response.text}")
                break
            else:
                print(f"Error sending command to Core IOT: {response.status_code}, {response.text}")
        except Exception as e:
            print(f"Exception when calling Core IOT API: {str(e)}")
        if attempt < max_retries - 1:
            time.sleep(1)
    
    print(value_data)
    
    return {
        'message': 'Create scheduler successful',
        'data': {
            'email': email_user,
            'relayName': relayName,
            'timeStart': timeStart,
            'timeEnd': timeEnd,
            'repeatDaily': repeatDaily,
            'timestamp': vietnam_time
        }
    }, 200


def service_get_setup_scheduler():
    # Lấy tất cả dữ liệu từ MongoDB
    schedulerList = list(collection_setup_scheduler.find())  # ✅ Convert Cursor thành list

    vietnam_tz = pytz.timezone('Asia/Ho_Chi_Minh')

    # Kiểm tra nếu không có dữ liệu
    if not schedulerList:  
        return {
            'message': 'No scheduler found in system', 
            'errCode': 1
        }, 400
    
    # Chuyển đổi dữ liệu thành danh sách dictionary
    scheduler_data_list = [
        {
            "id": str(scheduler["_id"]),
            "relayName": scheduler["relayName"],
            "timeStart": scheduler["timeStart"],
            "timeEnd": scheduler["timeEnd"],
            "timestamp": (
                # Nếu timestamp là datetime object
                (
                    # Nếu timestamp đã có timezone info
                    scheduler["timestamp"].astimezone(vietnam_tz) if scheduler["timestamp"].tzinfo
                    # Nếu timestamp không có timezone info, giả định là UTC
                    else pytz.UTC.localize(scheduler["timestamp"]).astimezone(vietnam_tz)
                ).strftime("%Y-%m-%dT%H:%M:%S")
                if isinstance(scheduler["timestamp"], datetime)
                else scheduler["timestamp"]
            ),
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

    vietnam_tz = pytz.timezone('Asia/Ho_Chi_Minh')

    # Kiểm tra nếu không có dữ liệu
    if not scheduler:  
        return {
            'message': 'No scheduler found in system', 
            'errCode': 1
        }, 400
    
    if scheduler["timestamp"].tzinfo is None:
        # Assume MongoDB timestamp is in UTC
        utc_time = scheduler["timestamp"].replace(tzinfo=pytz.UTC)
    else:
        utc_time = scheduler["timestamp"]

    # Convert to Vietnam time
    vietnam_time = utc_time.astimezone(vietnam_tz)
    print(vietnam_time)

    return {
        'message': 'Get scheduler By ID successful',
        'data': {
            'email': scheduler["email"],
            'relayName': scheduler["relayName"],
            'timeStart': scheduler["timeStart"],
            'timeEnd': scheduler["timeEnd"],
            'timestamp': vietnam_time.strftime("%Y-%m-%dT%H:%M:%S") 
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

    vietnam_tz = pytz.timezone('Asia/Ho_Chi_Minh')

    return {
        'message': 'Update scheduler successful',
        'data': {
                'email_user': updated_scheduler.get('email_user'),
                'relayName': updated_scheduler.get("relayName"),
                'timeStart': updated_scheduler.get("timeStart"),
                'timeEnd': updated_scheduler.get("timeEnd"),
                'timestamp': updated_scheduler["timestamp"].astimezone(vietnam_tz).strftime("%Y-%m-%dT%H:%M:%S") 
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