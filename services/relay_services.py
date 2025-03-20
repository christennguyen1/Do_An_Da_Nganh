from databases.databases import *
from datetime import datetime
from constant.constant import nutnhan
import pytz
from schemas import RelayData


import requests
import pytz
from datetime import datetime
import json
import time

def service_update_relay(body):
    # Extract data from request body
    data = body
    email_user = data.get('email_user')
    relay_name = data.get('relayName')
    status_relay = data.get('status')
    
    # Check if relay exists
    if relay_name not in nutnhan:
        return {
            'message': 'Relay not in server',
            'errCode': 1
        }, 400
    
    # Get current time in Vietnam timezone
    vietnam_tz = pytz.timezone('Asia/Ho_Chi_Minh')
    vietnam_time = datetime.now(vietnam_tz)
    
    # Prepare data for MongoDB
    data = {
        'email_user': email_user,
        'relayName': relay_name,
        'status': status_relay,
        'timestamp': vietnam_time
    }
    
    # Check if relay exists in MongoDB
    relay = collection_relay.find_one({'relayName': relay_name, 'email_user': email_user})
    print(relay)
    
    if relay == None:
        return {
            'message': 'Relay not in system',
            'errCode': 1
        }, 400
    
    # Update relay status in MongoDB
    query = {"relayName": relay_name, 'email_user': email_user}
    new_values = {
        "$set": {
            "status": status_relay, 
            "timestamp": vietnam_time
        }
    }
    
    collection_relay.update_one(query, new_values)
    
    # Now send command to Core IOT
    # Extract relay number from relay name (assuming format like "Relay1")
    relay_number = ""
    for char in relay_name:
        if char.isdigit():
            relay_number += char
    
    if not relay_number:
        relay_number = "1"  # Default to Relay1 if no number found
    
    # Prepare Core IOT API call
    core_iot_url = "https://app.coreiot.io/api/plugins/telemetry/DEVICE/21c4e8a0-f63f-11ef-a887-6d1a184f2bb5/SHARED_SCOPE"
    core_iot_body = {
        "method": f"setDataRelay{relay_number}",
        "value": status_relay == "ON"  # Convert string "ON"/"OFF" to boolean true/false
    }
    
    # Initial token from your input
    token = "eyJhbGciOiJIUzUxMiJ9.eyJzdWIiOiJ2aW5oLm5ndXllbjEyM0BoY211dC5lZHUudm4iLCJ1c2VySWQiOiJjOWY5OGNmMC1lMTQ2LTExZWYtYWQwOS01MTVmNzkwZWQ5ZGYiLCJzY29wZXMiOlsiVEVOQU5UX0FETUlOIl0sInNlc3Npb25JZCI6ImU4MzU5YzgxLWQ2NmEtNDljYi05NjgyLWE3MTg0MDFlOTQ4YyIsImV4cCI6MTc0MjAyMDQzMSwiaXNzIjoiY29yZWlvdC5pbyIsImlhdCI6MTc0MjAxMTQzMSwiZmlyc3ROYW1lIjoiVklOSCIsImxhc3ROYW1lIjoiTkdVWeG7hE4gS0jhuq5DIiwiZW5hYmxlZCI6dHJ1ZSwiaXNQdWJsaWMiOmZhbHNlLCJ0ZW5hbnRJZCI6ImM5ZTk4NzYwLWUxNDYtMTFlZi1hZDA5LTUxNWY3OTBlZDlkZiIsImN1c3RvbWVySWQiOiIxMzgxNDAwMC0xZGQyLTExYjItODA4MC04MDgwODA4MDgwODAifQ.mS-l5RJ-zRfHzJ237nGnnBNidf2KsQqnb0mgJWJtw8voOdkpMlOH3wuQvUtaKIV9qn8BZhr60E_DRrCzaDvp7w"
    headers = {
        "Content-Type": "application/json",
        "X-Authorization": f"Bearer {token}"
    }
    
    # Try to send command to Core IOT, handle token expiration
    max_retries = 2
    for attempt in range(max_retries):
        try:
            response = requests.post(core_iot_url, headers=headers, json=core_iot_body)
            
            # Check if token expired
            if response.status_code == 401 and "Token has expired" in response.text:
                print("Token expired, getting new token...")
                
                # Get new token
                login_url = "https://app.coreiot.io/api/auth/login"
                login_body = {
                    "username": "vinh.nguyen123@hcmut.edu.vn",
                    "password": "Vinhnguyen1$"
                }
                
                login_response = requests.post(login_url, json=login_body)
                if login_response.status_code == 200:
                    # Extract new token from response
                    login_data = login_response.json()
                    token = login_data.get('token')
                    
                    # Update headers with new token
                    headers["X-Authorization"] = f"Bearer {token}"
                    
                    # Retry with new token
                    continue
                else:
                    print(f"Failed to get new token: {login_response.text}")
            
            # If successful or other error
            if response.status_code == 200:
                print(f"Successfully sent command to Core IOT: {response.text}")
                break
            else:
                print(f"Error sending command to Core IOT: {response.status_code}, {response.text}")
                
        except Exception as e:
            print(f"Exception when calling Core IOT API: {str(e)}")
        
        # Wait before retry if not last attempt
        if attempt < max_retries - 1:
            time.sleep(1)
    
    # Return success response even if Core IOT call failed (MongoDB was updated)
    return {
        'message': 'Relay update successful',
        'data': {
            'email_user': email_user,
            'relayName': relay_name,
            'status': status_relay,
            'timestamp': vietnam_time
        }
    }, 200

    
def service_get_relay(body):
    data = body

    print(data)

    email_user = data.get('email_user')
    relay_name = data.get('relayName')

    if relay_name not in nutnhan:
        return {
                'message': 'Relay not in server', 
                'errCode': 1
            }, 400
    
    print(relay_name)
    

    relay = collection_relay.find_one({'relayName': relay_name, 'email_user': email_user})

    if relay == None:
        return {
                'message': 'Relay not in system', 
                'errCode': 1
            }, 400
        
    return {
        'message': 'Get Relay successful',
        'data': {
            'relayName': relay["relayName"],
            'status': relay["status"]
        }
    }, 200


def service_delete_relay(body):
    data = body

    print(data)

    email_user = data.get('email_user')
    relay_name = data.get('relayName')

    if relay_name not in nutnhan:
        return {
                'message': 'Relay not in server', 
                'errCode': 1
            }, 400
    
    relay = collection_relay.find_one({'relayName': relay_name, 'email_user': email_user})

    if relay == None:
        return {
                'message': 'Relay not in system', 
                'errCode': 1
            }, 400
    

    relay = collection_relay.delete_one({'relayName': relay_name, 'email_user': email_user})

    if relay == None:
        return {
                'message': 'Relay not in system', 
                'errCode': 1
            }, 400
        
    return {
        'message': 'Delete Relay successful',
        'data': {
            'relayName': relay_name
        }
    }, 200


def service_create_relay(body):
    data = body

    email_user = data.get('email_user')
    relay_name = data.get('relayName')
    status_relay = data.get('status')

    if collection_user.count_documents({"email": email_user}) == 0:
        return {
            'message': 'User was not registed',
            'data': []
        }, 200

    if relay_name not in nutnhan:
        return {
                'message': 'Relay not in server', 'errCode': 1
            }, 400
    
    vietnam_tz = pytz.timezone('Asia/Ho_Chi_Minh')
    vietnam_time = datetime.now(vietnam_tz)
    
    data = {
        'email_user': email_user,
        'relayName': relay_name,
        'status': status_relay,
        'timestamp': vietnam_time,
        'isDeleted': False
    }

    relay = collection_relay.find_one({'relayName': relay_name, 'email_user': email_user})

    if relay:
        query = {"relayName": relay_name, 'email_user': email_user}
        new_values = {
            "$set": {
                'status': status_relay, "isDeleted": False, "timestamp": vietnam_time
            }
        }
            
        collection_relay.update_one(query, new_values)
    else:
        if relay_name not in nutnhan:
            return {
                    'message': 'Relay was not setted up', 
                    'errCode': 1
                }, 400
        
    collection_relay.insert_one(data)

    publish_to_adafruit(relay_name, 1 if status_relay == "ON" else 0)
        
    return {
        'message': 'Create Relay successful',
        'data': {
            'email_user': email_user,
            'relayName': relay_name,
            'status': status_relay,
            'timestamp': vietnam_time
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
    
    relay_data_list = [
        RelayData(
            relayName=relay["relayName"],
            email_user=relay["email_user"],
            status=relay["status"],
            timestamp=relay["timestamp"].strftime("%Y-%m-%dT%H:%M:%S") if isinstance(relay["timestamp"], datetime) else relay["timestamp"],
        )
        for relay in relayList
    ]

    print(relay_data_list)
        
    return {
        'message': 'Get Relay successful',
        'data': relay_data_list
    }, 200
