from databases.databases import *
from datetime import datetime
from constant.constant import nutnhan


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

    data = {
        'email_user': email_user,
        'value': temperature_value,
        'status': status,
        'timestamp': datetime.now(),
    }

    collection_setup_temperature.insert_one(data)
    
    publish_to_adafruit("va-tem", temperature_value if status == "ON" else 0)
        
    return {
        'message': 'Create Relay successful',
        'data': {
            'email_user': email_user,
            'value': temperature_value,
            'status': status,
            'timestamp': datetime.now(),
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

    data = {
        'email_user': email_user,
        'value': pir_value,
        'status': status,
        'timestamp': datetime.now(),
    }

    collection_setup_pir.insert_one(data)

    publish_to_adafruit("va-pir", pir_value if status == "ON" else 0)
        
    return {
        'message': 'Create Relay successful',
        'data': {
            'email_user': email_user,
            'value': pir_value,
            'status': status,
            'timestamp': datetime.now(),
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

    data = {
        'email_user': email_user,
        'value': light_value,
        'status': status,
        'timestamp': datetime.now(),
    }

    collection_setup_light.insert_one(data)

    publish_to_adafruit("va-lux", light_value if status == "ON" else 0)
        
    return {
        'message': 'Create Set up light successful',
        'data': {
            'email_user': email_user,
            'value': light_value,
            'status': status,
            'timestamp': datetime.now(),
        }
    }, 200