from fastapi import APIRouter, Depends
from fastapi.security import OAuth2PasswordBearer
from controller.sensors_controller import controller_get_data

router = APIRouter()


# oauth2_scheme = OAuth2PasswordBearer(tokenUrl="signin")


# @router.get("/all/{user}")
# async def get_sensor_data(user: str, token: str = Depends(oauth2_scheme)):
#     return controller_get_data(user, token)

@router.get("/all/{user}")
async def get_sensor_data(user: str):
    return controller_get_data(user)