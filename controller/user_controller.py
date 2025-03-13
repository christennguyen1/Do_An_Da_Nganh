from fastapi import Request
from services.user_services import service_user_register, service_user_updatePassword, service_user_updateInfo, service_user_getInfo
from fastapi.responses import JSONResponse
from authenticate.jwt_handler import verify_jwt_token

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
    


    
def controller_get_user_info(user: str):
    try:
        # Truy vấn tất cả các document trong collection
        # payload = verify_jwt_token(token)
        print("Hello2")
        data, status = service_user_getInfo(user)
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
