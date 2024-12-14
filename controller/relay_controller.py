from authenticate.jwt_handler import verify_jwt_token
from services.relay_services import service_update_relay, service_create_relay
from fastapi.responses import JSONResponse
from fastapi.encoders import jsonable_encoder

# Update relay status
def controller_update_relay(body):
# Xác thực token
    try:
        # Truy vấn tất cả các document trong collection
        # payload = verify_jwt_token(token)
        data, status = service_update_relay(body)
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
    

# Create new relay
def controller_create_relay(body):
# Xác thực token
    try:
        # Truy vấn tất cả các document trong collection
        # payload = verify_jwt_token(token)
        data, status = service_create_relay(body)
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