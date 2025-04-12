from databases.databases import *
from constant.constant import nutnhan
from schemas import RelayData
from pymongo  import DESCENDING
import requests
import pytz
from datetime import datetime
import json
import time


def service_update_relay(body):
    data = body
    email_user = data.get('email_user')  # Vẫn giữ để ghi log nếu cần
    relay_name = data.get('relayName')
    status_relay = data.get('status')
   
    if relay_name not in nutnhan:
        return {'message': 'Relay not in server', 'errCode': 1}, 400
   
    vietnam_tz = pytz.timezone('Asia/Ho_Chi_Minh')
    vietnam_time = datetime.now(vietnam_tz)
   
    # Dữ liệu cập nhật không phụ thuộc email_user
    data = {
        'relayName': relay_name,
        'email_user': email_user,
        'status': status_relay,
        'timestamp': vietnam_time,
        'updated_by': email_user  # Lưu email_user như thông tin phụ
    }
   
    # Tìm relay dựa trên relayName duy nhất
    relay = collection_relay.find_one({'relayName': relay_name})
   
    # if relay is None:
        # Tạo mới nếu chưa tồn tại
    collection_relay.insert_one(data)
    # else:
    #     # Cập nhật trạng thái
    #     query = {"relayName": relay_name}
    #     new_values = {
    #         "$set": {
    #             "status": status_relay,
    #             "timestamp": vietnam_time,
    #             "updated_by": email_user
    #         }
    #     }
    #     collection_relay.update_one(query, new_values)
   
    # Gửi lệnh đến Core IOT
    relay_number = relay_name.split("nutnhan")
    print(relay_number)
    core_iot_url = "https://app.coreiot.io/api/plugins/telemetry/DEVICE/21c4e8a0-f63f-11ef-a887-6d1a184f2bb5/SHARED_SCOPE"
    core_iot_body = {
        "method": f"setDataRelay{relay_number[1]}",
        "value": status_relay == "ON"
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
        'message': 'Relay update successful',
        'data': {
            'relayName': relay_name,
            'status': status_relay,
            'timestamp': vietnam_time,
            'updated_by': email_user
        }
    }, 200
   
def service_get_relay(body):
    data = body
    relay_name = data.get('relayName')
    
    if relay_name not in nutnhan:
        return {'message': 'Relay not in server', 'errCode': 1}, 400
    
    # Trực tiếp tìm bản ghi có thời gian lớn nhất
    latest_relay = collection_relay.find(
        {'relayName': relay_name}
    ).sort('timestamp', -1).limit(1)
    
    latest_relay_doc = next(latest_relay, None)
    
    if latest_relay_doc is None:
        return {'message': 'Relay not in system', 'errCode': 1}, 400
    
    # Loại bỏ trường _id (nếu không muốn trả về)
    if '_id' in latest_relay_doc:
        latest_relay_doc.pop('_id')
    
    return {
        'message': 'Get Relay successful',
        'data': latest_relay_doc
    }, 200


def service_getAllStatus_relay(body):
    relay_names = ['nutnhan_1', 'nutnhan_2', 'nutnhan_3', 'nutnhan_4']
    latest_relay_status = {}
    vietnam_tz = pytz.timezone('Asia/Ho_Chi_Minh')
    for relay_name in relay_names:
        relay = collection_relay.find_one(
            {'relayName': relay_name},
            sort=[('timestamp', DESCENDING)]
        )
        if relay["timestamp"].tzinfo is None:
            # Assume MongoDB timestamp is in UTC
            utc_time = relay["timestamp"].replace(tzinfo=pytz.UTC)
        else:
            utc_time = relay["timestamp"]

        # Convert to Vietnam time
        vietnam_time = utc_time.astimezone(vietnam_tz)
        print(vietnam_time)
        if relay:
            latest_relay_status[relay_name] = {
                'status': relay['status'],
                'timestamp': vietnam_time.strftime("%Y-%m-%dT%H:%M:%S") 
                if isinstance(relay["timestamp"], datetime) else relay["timestamp"],
                'updated_by': relay.get('updated_by', 'Unknown')
            }
        else:
            latest_relay_status[relay_name] = {
                'status': 'OFF',
                'timestamp': None,
                'updated_by': 'Unknown'
            }
    return {
        'message': 'Get Relay successful',
        'data': latest_relay_status
    }, 200

def service_delete_relay(body):
    data = body
    relay_name = data.get('relayName')


    if relay_name not in nutnhan:
        return {'message': 'Relay not in server', 'errCode': 1}, 400
   
    relay = collection_relay.find_one({'relayName': relay_name})
    if relay is None:
        return {'message': 'Relay not in system', 'errCode': 1}, 400
   
    collection_relay.delete_one({'relayName': relay_name})
    return {
        'message': 'Delete Relay successful',
        'data': {'relayName': relay_name}
    }, 200


def service_create_relay(body):
    data = body
    email_user = data.get('email_user')
    relay_name = data.get('relayName')
    status_relay = data.get('status')


    if relay_name not in nutnhan:
        return {'message': 'Relay not in server', 'errCode': 1}, 400
   
    vietnam_tz = pytz.timezone('Asia/Ho_Chi_Minh')
    vietnam_time = datetime.now(vietnam_tz)
   
    data = {
        'relayName': relay_name,
        'status': status_relay,
        'timestamp': vietnam_time,
        'email_user': email_user
    }


    relay = collection_relay.find_one({'relayName': relay_name})
    if relay:
        query = {"relayName": relay_name}
        new_values = {"$set": {'status': status_relay, "timestamp": vietnam_time, "updated_by": email_user}}
        collection_relay.update_one(query, new_values)
    else:
        collection_relay.insert_one(data)


    return {
        'message': 'Create Relay successful',
        'data': {
            'relayName': relay_name,
            'status': status_relay,
            'timestamp': vietnam_time,
            'email_user': email_user
        }
    }, 200




def service_get_relay_history(body):
    data = body
    relay_name = data.get('relayName')


    if relay_name not in nutnhan:
        return {
                'message': 'Relay not in server',
                'errCode': 1
            }, 400
   
    print(relay_name)
   


    relayList = collection_relay.find({'relayName': relay_name})


    if relayList == None:
        return {
                'message': 'Relay not in system',
                'errCode': 1
            }, 400
    
    vietnam_tz = pytz.timezone('Asia/Ho_Chi_Minh')
   
    relay_data_list = [
        RelayData(
            relayName=relay["relayName"],
            email_user=relay["email_user"],
            status=relay["status"],
            timestamp=(
                # Nếu timestamp là datetime object
                (
                    # Nếu timestamp đã có timezone info
                    relay["timestamp"].astimezone(vietnam_tz) if relay["timestamp"].tzinfo
                    # Nếu timestamp không có timezone info, giả định là UTC
                    else pytz.UTC.localize(relay["timestamp"]).astimezone(vietnam_tz)
                ).strftime("%Y-%m-%dT%H:%M:%S")
                if isinstance(relay["timestamp"], datetime)
                else relay["timestamp"]
            ),
        )
        for relay in relayList
    ]


    print(relay_data_list)
       
    return {
        'message': 'Get Relay successful',
        'data': relay_data_list
    }, 200



