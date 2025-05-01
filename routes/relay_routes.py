from fastapi import APIRouter, Depends, Request, Query
from fastapi.responses import JSONResponse
from controller.relay_controller import (
    controller_update_relay,
    controller_create_relay,
    controller_get_relay,
    controller_delete_relay,
    controller_get_relay_history,
    controller_getAllStatus_relay
)
from fastapi.security import OAuth2PasswordBearer
from fastapi.encoders import jsonable_encoder
from middleware.websocket_manager import broadcast_relay_update
import json


router = APIRouter()
oauth2_scheme = OAuth2PasswordBearer(tokenUrl="signin")


async def get_all_status_for_broadcast(email_user: str):
    try:
        response = controller_getAllStatus_relay({"email_user": email_user})
        if isinstance(response, JSONResponse):
            return json.loads(response.body.decode('utf-8'))
        elif isinstance(response, tuple) and response[1] == 200:
            return response[0]
        return None
    except Exception as e:
        print(f"Error fetching all status for broadcast: {e}")
        return None


@router.post("/update")
async def update_relay_data(request: Request):
    body = await request.json()
    response = controller_update_relay(body)
   
    if isinstance(response, JSONResponse):
        if response.status_code == 200:
            response_data = json.loads(response.body.decode('utf-8'))
            all_status_response = await get_all_status_for_broadcast(body.get("email_user"))
            if all_status_response and all_status_response.get("data"):
                await broadcast_relay_update(all_status_response)
        return response
    else:
        response_dict, status_code = response
        if status_code == 200:
            all_status_response = await get_all_status_for_broadcast(body.get("email_user"))
            if all_status_response and all_status_response.get("data"):
                await broadcast_relay_update(all_status_response)
        return JSONResponse(content=response_dict, status_code=status_code)


@router.get("/getStatus")
async def get_relay_data(request: Request):
    body = await request.json()
    return controller_get_relay(body)


@router.get("/getAllStatus")
async def get_all_relay_data(email_user: str):
    return controller_getAllStatus_relay({"email_user": email_user})


@router.get("/getHistory")
async def get_relay_data_history(request: Request):
    body = await request.json()
    return controller_get_relay_history(body)


@router.post("/create")
async def create_relay_data(request: Request):
    body = await request.json()
    return controller_create_relay(body)


@router.delete("/delete")
async def delete_relay_data(request: Request):
    body = await request.json()
    response = controller_delete_relay(body)
   
    if isinstance(response, JSONResponse):
        if response.status_code == 200:
            all_status_response = await get_all_status_for_broadcast(body.get("email_user"))
            if all_status_response and all_status_response.get("data"):
                await broadcast_relay_update(all_status_response)
        return response
    else:
        response_dict, status_code = response
        if status_code == 200:
            all_status_response = await get_all_status_for_broadcast(body.get("email_user"))
            if all_status_response and all_status_response.get("data"):
                await broadcast_relay_update(all_status_response)
        return JSONResponse(content=response_dict, status_code=status_code)





# POST http://localhost:8000/api/ai-simulator/monitor/single
# Content-Type: application/json

# {
#   "user_id": 1,
#   "device": "Cảm biến nhiệt độ A1",
#   "description": "Nhiệt độ cao bất thường",
#   "severity": "Cao", 
#   "issue": "Nhiệt độ quá cao",
#   "recommendation": "Tăng cường hệ thống làm mát",
#   "message": "Cảnh báo: Phát hiện nhiệt độ cao bất thường tại khu vực trồng lúa"
# }