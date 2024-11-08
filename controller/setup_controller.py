from authenticate.jwt_handler import verify_jwt_token
from services.setup_services import service_setup_temperature, service_setup_pir, service_setup_light
from fastapi.responses import JSONResponse
from fastapi.encoders import jsonable_encoder

def controller_setup_temperature(body, token: str):
# Xác thực token
    try:
        # Truy vấn tất cả các document trong collection
        payload = verify_jwt_token(token)
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


def controller_setup_pir(body, token: str):
# Xác thực token
    try:
        # Truy vấn tất cả các document trong collection
        payload = verify_jwt_token(token)
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
    


def controller_setup_light(body, token: str):
# Xác thực token
    try:
        # Truy vấn tất cả các document trong collection
        payload = verify_jwt_token(token)
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
    