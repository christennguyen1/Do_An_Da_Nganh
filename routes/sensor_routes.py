from fastapi import APIRouter, Depends
from fastapi.security import OAuth2PasswordBearer
from controller.sensors_controller import controller_get_data, controller_get_data_month, controller_get_data_week, controller_get_data_day

router = APIRouter()


# oauth2_scheme = OAuth2PasswordBearer(tokenUrl="signin")


# @router.get("/all/{user}")
# async def get_sensor_data(user: str, token: str = Depends(oauth2_scheme)):
#     return controller_get_data(user, token)

@router.get("/latest/{user}")
async def get_sensor_data(user: str):
    return controller_get_data(user)


@router.get("/all/month/{user}")
async def get_sensor_data_month(user: str):
    return controller_get_data_month(user)

@router.get("/all/week/{user}")
async def get_sensor_data_week(user: str):
    return controller_get_data_week(user)

@router.get("/all/day/{user}")
async def get_sensor_data_day(user: str):
    return controller_get_data_day(user)

