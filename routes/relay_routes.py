from fastapi import APIRouter,  Depends, Request
from controller.relay_controller import controller_update_relay, controller_create_relay, controller_get_relay, controller_delete_relay, controller_get_relay_history,controller_getAllStatus_relay
from fastapi.security import OAuth2PasswordBearer


router = APIRouter()
# oauth2_scheme = OAuth2PasswordBearer(tokenUrl="signin")


# @router.post("/update")
# async def update_relay_data(request: Request, token: str = Depends(oauth2_scheme)):
#     body = await request.json()
#     return controller_update_relay(body, token)


# @router.get("/getStatus")
# async def get_relay_data(request: Request, token: str = Depends(oauth2_scheme)):
#     body = await request.json()
#     return controller_get_relay(body, token)


# @router.post("/create")
# async def update_relay_data(request: Request, token: str = Depends(oauth2_scheme)):
#     body = await request.json()
#     return controller_create_relay(body, token)


# @router.delete("/delete")
# async def delete_relay_data(request: Request, token: str = Depends(oauth2_scheme)):
#     body = await request.json()
#     return controller_delete_relay(body, token)


@router.post("/update")
async def update_relay_data(request: Request):
    body = await request.json()
    return controller_update_relay(body)


@router.get("/getStatus")
async def get_relay_data(request: Request):
    body = await request.json()
    return controller_get_relay(body)


@router.get("/getAllStatus")
async def get_relay_data(request: Request):
    body = await request.json()
    return controller_getAllStatus_relay(body)

@router.get("/getHistory")
async def get_relay_data_history(request: Request):
    body = await request.json()
    return controller_get_relay_history(body)


@router.post("/create")
async def update_relay_data(request: Request):
    body = await request.json()
    return controller_create_relay(body)


@router.delete("/delete")
async def delete_relay_data(request: Request):
    body = await request.json()
    return controller_delete_relay(body)