from fastapi import APIRouter,  Depends, Request
from controller.relay_controller import controller_update_relay, controller_create_relay
from fastapi.security import OAuth2PasswordBearer


router = APIRouter()
oauth2_scheme = OAuth2PasswordBearer(tokenUrl="signin")


@router.post("/update")
async def update_relay_data(request: Request, token: str = Depends(oauth2_scheme)):
    body = await request.json()
    return controller_update_relay(body, token)



@router.post("/create")
async def update_relay_data(request: Request, token: str = Depends(oauth2_scheme)):
    body = await request.json()
    return controller_create_relay(body, token)