from fastapi import APIRouter,  Depends, Request
from controller.setup_controller import  controller_get_setup_scheduler, controller_get_setup_scheduler_ByID, controller_update_scheduler, controller_delete_scheduler, controller_put_setup_threshold,controller_delete_setup_scheduler, controller_get_setup_scheduler
from fastapi.security import OAuth2PasswordBearer


router = APIRouter()
oauth2_scheme = OAuth2PasswordBearer(tokenUrl="signin")




@router.put("/threshold")
async def create_setup_threshold(request: Request):
    body = await request.json()
    return controller_put_setup_threshold(body)

@router.delete("/threshold")
async def delete_setup_threshold():
    return controller_delete_setup_scheduler()

@router.get("/threshold")
async def get_setup_threshold():
    return controller_get_setup_scheduler()


@router.get("/scheduler")
async def get_setup_scheduler():
    return controller_get_setup_scheduler()


@router.get("/schedulerById")
async def get_setup_schedulerById(request: Request):
    body = await request.json()
    return controller_get_setup_scheduler_ByID(body)


@router.put("/scheduler")
async def update_setup_scheduler(request: Request):
    body = await request.json()
    print("hello1: ", body)
    return controller_update_scheduler(body)

@router.delete("/scheduler")
async def create_setup_scheduler(request: Request):
    body = await request.json()
    print("hello1: ", body)
    return controller_delete_scheduler(body)


