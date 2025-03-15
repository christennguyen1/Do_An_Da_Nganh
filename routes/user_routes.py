from middleware.middleware import periodic_data_collection
from fastapi import APIRouter,  Depends, Request
from controller.auth_controller import controller_signin
from controller.user_controller import controller_signup, controller_updatePassword, controller_updateInfo, controller_get_user_info
from fastapi.security import OAuth2PasswordBearer
import asyncio
from authenticate.jwt_handler import verify_jwt_token, refresh_access_token


router = APIRouter()
oauth2_scheme = OAuth2PasswordBearer(tokenUrl="signin")


@router.get("/info")
async def get_user_info(token: str = Depends(oauth2_scheme)):
    print("Hello1")
    return controller_get_user_info(token)

# @router.get("/info")
# async def get_user_info(request: Request):
#     body = await request.json()
#     print(body)
#     return controller_get_user_info(body)


@router.post("/signin")
async def signin_route(request: Request):
    body = await request.json()
    return controller_signin(body)


@router.post("/signup")
async def signup_route(request: Request):
    body = await request.json()
    return controller_signup(body)


@router.put("/updatePassword")
async def updatePassword_route(request: Request):
    body = await request.json()
    return controller_updatePassword(body)


@router.put("/updateInfo")
async def updateInfo_route(request: Request):
    body = await request.json()
    return controller_updateInfo(body)


@router.post("/refresh-token")
def refresh_token(token: str = Depends(oauth2_scheme)):
    return refresh_access_token(token)


# @router.get("/get-message")
# async def get_message(token: str = Depends(oauth2_scheme)):
#     username = verify_jwt_token(token)
#     return {"message": f"Chào mừng {username} đến với hệ thống!"}


@router.on_event("startup")
async def start_periodic_collection():
    asyncio.create_task(periodic_data_collection())