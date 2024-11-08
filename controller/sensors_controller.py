from authenticate.jwt_handler import verify_jwt_token
from services.sensors_services import service_get_all_data
from fastapi.responses import JSONResponse

def controller_get_data(user: str, token: str):
# Xác thực token
    try:
        # Truy vấn tất cả các document trong collection
        payload = verify_jwt_token(token)
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

    