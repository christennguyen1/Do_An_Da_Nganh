from fastapi import HTTPException
from fastapi.encoders import jsonable_encoder  # Thêm thư viện này
from databases.databases import *
from schemas import SensorData
import asyncio


def service_get_all_data(user: str):
    sensors = collection_sensor.find({"user": user})
    
    # Nếu không có dữ liệu cảm biến nào cho người dùng
    if collection_sensor.count_documents({"user": user}) == 0:
        return {
            'message': 'Data or user do not have data',
            'data': []
        }, 200

    # Tạo danh sách dữ liệu cảm biến
    sensor_data_list = [
        SensorData(lux=sensor["lux"], temperature=sensor["temperature"], humidity=sensor["humidity"]) 
        for sensor in sensors
    ]

    # Chuyển đổi dữ liệu thành JSON
    response_data = {
        "total_data": len(sensor_data_list),
        "sensor_data": jsonable_encoder(sensor_data_list)  # Chuyển dữ liệu thành JSON
    }

    # Trả về dữ liệu JSON
    return {
        'message': 'Get all data successfully',
        'data': response_data
    }, 200