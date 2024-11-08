from fastapi import APIRouter,  Depends, Request
from controller.setup_controller import controller_setup_temperature, controller_setup_pir, controller_setup_light
from fastapi.security import OAuth2PasswordBearer


router = APIRouter()
oauth2_scheme = OAuth2PasswordBearer(tokenUrl="signin")


@router.post("/temperature")
async def create_setup_temperature(request: Request, token: str = Depends(oauth2_scheme)):
    body = await request.json()
    return controller_setup_temperature(body, token)



@router.post("/pir")
async def create_setup_pir(request: Request, token: str = Depends(oauth2_scheme)):
    body = await request.json()
    return controller_setup_pir(body, token)



@router.post("/light")
async def create_setup_light(request: Request, token: str = Depends(oauth2_scheme)):
    body = await request.json()
    return controller_setup_light(body, token)