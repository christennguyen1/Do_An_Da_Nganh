from fastapi import HTTPException
from fastapi.encoders import jsonable_encoder  # Thêm thư viện này
from databases.databases import *
from schemas import SensorData
import asyncio
from datetime import datetime, timedelta, timezone


# def service_get_all_data(user: str):
#     sensors = collection_sensor.find({"user": user})
    
#     # Nếu không có dữ liệu cảm biến nào cho người dùng
#     if collection_sensor.count_documents({"user": user}) == 0:
#         return {
#             'message': 'Data or user do not have data',
#             'data': []
#         }, 200

#     # Tạo danh sách dữ liệu cảm biến
#     sensor_data_list = [
#         SensorData(lux=sensor["lux"], temperature=sensor["temperature"], humidity=sensor["humidity"], timestamp = sensor["timestamp"]) 
#         for sensor in sensors
#     ]

#     # Chuyển đổi dữ liệu thành JSON
#     response_data = {
#         "total_data": len(sensor_data_list),
#         "sensor_data": jsonable_encoder(sensor_data_list)  # Chuyển dữ liệu thành JSON
#     }

#     # Trả về dữ liệu JSON
#     return {
#         'message': 'Get all data successfully',
#         'data': response_data
#     }, 200



def service_get_all_data(user: str):
    # Tính thời gian bắt đầu và kết thúc cho khoảng thời gian 1 tuần
    start_date = (datetime.now(timezone.utc) - timedelta(weeks=1)).strftime("%Y-%m-%dT%H:%M:%SZ")

    # Lấy thời gian hiện tại
    end_date = datetime.now(timezone.utc).strftime("%Y-%m-%dT%H:%M:%SZ")

    # Debug thông tin thời gian
    print(f"Fetching data from {start_date} to {end_date} for user: {user}")

    sensors = collection_sensor.find({
        "user": user,
        "timestamp": {
                # "$gte": start_date,
                "$lte": end_date
            }  # Lọc dữ liệu có timestamp >= one_week_ago
    })
    
    # Nếu không có dữ liệu cảm biến nào cho người dùng
    if collection_sensor.count_documents({"user": user, "timestamp": {
        # "$gte": start_date,
        "$lte": end_date
    }}) == 0:
        return {
            'message': 'Data or user do not have data in the last week',
            'data': []
        }, 200

    # Tạo danh sách dữ liệu cảm biến
    sensor_data_list = [
        SensorData(
            lux=sensor["lux"], 
            temperature=sensor["temperature"], 
            humidity=sensor["humidity"], 
            timestamp=datetime.strptime(sensor["timestamp"], "%Y-%m-%dT%H:%M:%SZ").strftime("%Y-%m-%d-%H:%M:%S")  # Đảm bảo timestamp theo định dạng mong muốn
        ) 
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
