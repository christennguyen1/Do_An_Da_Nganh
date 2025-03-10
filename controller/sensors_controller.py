from authenticate.jwt_handler import verify_jwt_token
from services.sensors_services import service_get_all_data, service_get_all_data_month, service_get_all_data_week, service_get_all_data_day
from fastapi.responses import JSONResponse

# def controller_get_data(user: str, token: str):
def controller_get_data(user: str):
# Xác thực token
    try:
        # Truy vấn tất cả các document trong collection
        # verify_jwt_token(token)
        data, status = service_get_all_data(user)
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
    

# def controller_get_data(user: str, token: str):
def controller_get_data_month(user: str):
# Xác thực token
    try:
        # Truy vấn tất cả các document trong collection
        # verify_jwt_token(token)
        data, status = service_get_all_data_month(user)
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

# def controller_get_data(user: str, token: str):
def controller_get_data_week(user: str):
# Xác thực token
    try:
        # Truy vấn tất cả các document trong collection
        # verify_jwt_token(token)
        data, status = service_get_all_data_week(user)
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
    
# def controller_get_data(user: str, token: str):
def controller_get_data_day(user: str):
# Xác thực token
    try:
        # Truy vấn tất cả các document trong collection
        # verify_jwt_token(token)
        data, status = service_get_all_data_day(user)
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
    