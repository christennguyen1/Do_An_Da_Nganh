from middleware.middleware import periodic_data_collection
from fastapi import APIRouter,  Depends, Request
from controller.auth_controller import controller_signin
from controller.user_controller import controller_signup, controller_updatePassword, controller_updateInfo
from fastapi.security import OAuth2PasswordBearer
import asyncio
from services.auth_service import refresh_user_token
from authenticate.jwt_handler import verify_jwt_token


router = APIRouter()
oauth2_scheme = OAuth2PasswordBearer(tokenUrl="signin")


@router.post("/signin")
async def signin_route(request: Request):
    body = await request.json()
    return controller_signin(body)


@router.post("/signup")
async def signup_route(request: Request):
    body = await request.json()
    return controller_signup(body)


@router.post("/updatePassword")
async def updatePassword_route(request: Request):
    body = await request.json()
    return controller_updatePassword(body)


@router.post("/updateInfo")
async def updateInfo_route(request: Request):
    body = await request.json()
    return controller_updateInfo(body)


@router.post("/refresh-token")
def refresh_token(token: str = Depends(oauth2_scheme)):
    return refresh_user_token(token)


@router.get("/get-message")
async def get_message(token: str = Depends(oauth2_scheme)):
    username = verify_jwt_token(token)
    return {"message": f"Chào mừng {username} đến với hệ thống!"}


@router.on_event("startup")
async def start_periodic_collection():
    asyncio.create_task(periodic_data_collection())