from authenticate.jwt_handler import verify_jwt_token
from services.setup_services import service_setup_temperature, service_setup_pir, service_setup_light, service_create_setup_scheduler, service_get_setup_scheduler, service_get_setup_scheduler_ByID, service_update_setup_scheduler, service_delete_setup_scheduler
from fastapi.responses import JSONResponse
from fastapi.encoders import jsonable_encoder

def controller_setup_temperature(body, token):
# Xác thực token
    try:
        # Truy vấn tất cả các document trong collection
        verify_jwt_token(token)
        data, status = service_setup_temperature(body)
        response = {
            "message": data.get('message'),
            "data": jsonable_encoder(data.get('data')),
            "status": status,
            "errCode": 0
        }
        return JSONResponse(content=response, status_code=status)
    except Exception as e:
        return {
            "status": 500,
            "message": str(e),
            "error": 1
        }, 500


def controller_setup_pir(body, token):
# Xác thực token
    try:
        # Truy vấn tất cả các document trong collection
        verify_jwt_token(token)
        data, status = service_setup_pir(body)
        response = {
            "message": data.get('message'),
            "data": jsonable_encoder(data.get('data')),
            "status": status,
            "errCode": 0
        }
        return JSONResponse(content=response, status_code=status)
    except Exception as e:
        return {
            "status": 500,
            "message": str(e),
            "error": 1
        }, 500
    


def controller_setup_light(body, token):
# Xác thực token
    try:
        # Truy vấn tất cả các document trong collection
        verify_jwt_token(token)
        data, status = service_setup_light(body)
        response = {
            "message": data.get('message'),
            "data": jsonable_encoder(data.get('data')),
            "status": status,
            "errCode": 0
        }
        return JSONResponse(content=response, status_code=status)
    except Exception as e:
        return {
            "status": 500,
            "message": str(e),
            "error": 1
        }, 500
    

def controller_create_setup_scheduler(body):
# Xác thực token
    try:
        # Truy vấn tất cả các document trong collection
        # verify_jwt_token(token)
        print("Hello2: ", body)
        data, status = service_create_setup_scheduler(body)
        print("Hello5:", data)
        response = {
            "message": data.get('message'),
            "data": jsonable_encoder(data.get('data')),
            "status": status,
            "errCode": 0
        }
        return JSONResponse(content=response, status_code=status)
    except Exception as e:
        return {
            "status": 500,
            "message": str(e),
            "error": 1
        }, 500
    

def controller_get_setup_scheduler():
# Xác thực token
    try:
        # Truy vấn tất cả các document trong collection
        # verify_jwt_token(token)
        data, status = service_get_setup_scheduler()
        response = {
            "message": data.get('message'),
            "data": jsonable_encoder(data.get('data')),
            "status": status,
            "errCode": 0
        }
        return JSONResponse(content=response, status_code=status)
    except Exception as e:
        return {
            "status": 500,
            "message": str(e),
            "error": 1
        }, 500
    

def controller_get_setup_scheduler_ByID(body):
# Xác thực token
    try:
        # Truy vấn tất cả các document trong collection
        # verify_jwt_token(token)
        data, status = service_get_setup_scheduler_ByID(body)
        response = {
            "message": data.get('message'),
            "data": jsonable_encoder(data.get('data')),
            "status": status,
            "errCode": 0
        }
        return JSONResponse(content=response, status_code=status)
    except Exception as e:
        return {
            "status": 500,
            "message": str(e),
            "error": 1
        }, 500
    

def controller_update_scheduler(body):
# Xác thực token
    try:
        # Truy vấn tất cả các document trong collection
        # verify_jwt_token(token)
        data, status = service_update_setup_scheduler(body)
        response = {
            "message": data.get('message'),
            "data": jsonable_encoder(data.get('data')),
            "status": status,
            "errCode": 0
        }
        return JSONResponse(content=response, status_code=status)
    except Exception as e:
        return {
            "status": 500,
            "message": str(e),
            "error": 1
        }, 500
    

def controller_delete_scheduler(body):
# Xác thực token
    try:
        # Truy vấn tất cả các document trong collection
        # verify_jwt_token(token)
        data, status = service_delete_setup_scheduler(body)
        response = {
            "message": data.get('message'),
            "data": jsonable_encoder(data.get('data')),
            "status": status,
            "errCode": 0
        }
        return JSONResponse(content=response, status_code=status)
    except Exception as e:
        return {
            "status": 500,
            "message": str(e),
            "error": 1
        }, 500
    