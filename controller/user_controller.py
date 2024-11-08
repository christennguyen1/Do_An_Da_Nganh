from fastapi import Request
from services.user_services import service_user_register, service_user_updatePassword, service_user_updateInfo
from fastapi.responses import JSONResponse

def controller_signup(body):
    try:
        # Truy vấn tất cả các document trong collection
        data, status = service_user_register(body)
        response = {
            "message": data.get('message'),
            "data": data.get('data'),
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
    

def controller_updatePassword(body):
    try:
        # Truy vấn tất cả các document trong collection
        data, status = service_user_updatePassword(body)
        response = {
            "message": data.get('message'),
            "data": data.get('data'),
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
    

def controller_updateInfo(body):
    try:
        # Truy vấn tất cả các document trong collection
        data, status = service_user_updateInfo(body)
        response = {
            "message": data.get('message'),
            "data": data.get('data'),
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
