from services.auth_service import authenticate_user
from authenticate.jwt_handler import create_jwt_token, create_refresh_token
from fastapi import Request
from services.user_services import service_user_login
from fastapi.responses import JSONResponse

def controller_signin(body):
    try:
        # Truy vấn tất cả các document trong collection
        data, status = service_user_login(body)
        if status == 200 or status == 201:
            access_token = create_jwt_token({"sub": data.get('data')['Email']})
            refresh_token = create_refresh_token({"sub": data.get('data')['Email']})
        else:
            access_token = ""
            refresh_token = ""

        response = {
            "message": data.get('message'),
            "data": data.get('data'),
            "refresh_token": refresh_token,
            "access_token": access_token,
            "token_type": "Bearer",
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

