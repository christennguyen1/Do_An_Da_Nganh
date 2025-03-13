from databases.databases import *
from datetime import datetime
from constant.constant import nutnhan
import pytz


def service_update_relay(body):
    data = body

    email_user = data.get('email_user')
    relay_name = data.get('relayName')
    status_relay = data.get('status')

    if relay_name not in nutnhan:
        return {
                'message': 'Relay not in server', 
                'errCode': 1
            }, 400
    
    vietnam_tz = pytz.timezone('Asia/Ho_Chi_Minh')
    vietnam_time = datetime.now(vietnam_tz)
    
    data = {
        'email_user': email_user,
        'relayName': relay_name,
        'status': status_relay,
        'timestamp': vietnam_time
    }

    relay = collection_relay.find_one({'relayName': relay_name, 'email_user': email_user})

    print(relay)

    # relay_status_delete = relay.get('isDeleted', 'Unknown')

    # if ((not relay) or (relay_status_delete == True)):
    #     return {
    #             'message': 'Relay not in system', 
    #             'errCode': 1
    #         }, 400
    query = {"relayName": relay_name, 'email_user': email_user}
    new_values = {
        "$set": {
            "status": status_relay, "timestamp": vietnam_time
            }
        }
    
    collection_relay.update_one(query, new_values)
        
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

    print(relay)
        
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
    
    print(relay_name)
    

    relay = collection_relay.delete_one({'relayName': relay_name, 'email_user': email_user})

    print(relay)
        
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
        relay_status_delete = relay.get('isDeleted', 'Unknown')
        if relay_status_delete == False:
            return {
                    'message': 'Relay was setted up', 
                    'errCode': 1
                }, 400
        else:
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