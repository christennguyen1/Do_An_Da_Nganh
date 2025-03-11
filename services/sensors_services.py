from fastapi import HTTPException
from fastapi.encoders import jsonable_encoder  # Thêm thư viện này
from databases.databases import *
from schemas import SensorData, SensorDataWeek, SensorDataDay, SensorDataMonth
import asyncio
from datetime import datetime, timedelta, timezone
import pandas as pd
from dateutil.relativedelta import relativedelta



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
            lux=sensors[0]["lux"], 
            temperature=sensors[0]["temperature"], 
            humidity=sensors[0]["humidity"], 
            timestamp=datetime.strptime(sensors[0]["timestamp"], "%Y-%m-%dT%H:%M:%SZ").strftime("%Y-%m-%d-%H:%M:%S")  # Đảm bảo timestamp theo định dạng mong muốn
        ) 
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


def service_get_all_data_month(user: str):
    # Tính thời gian bắt đầu và kết thúc cho khoảng thời gian 1 tuần
    # Go back 12 months from the current date
    start_date = (datetime.now(timezone.utc) - relativedelta(months=12)).strftime("%Y-%m-%dT%H:%M:%SZ")

    # Lấy thời gian hiện tại
    end_date = datetime.now(timezone.utc).strftime("%Y-%m-%dT%H:%M:%SZ")

    # Debug thông tin thời gian
    print(f"Fetching data from {start_date} to {end_date} for user: {user}")

    sensors = collection_sensor.find({
        "user": user,
        "timestamp": {
                "$gte": start_date,
                "$lte": end_date
            }  # Lọc dữ liệu có timestamp >= one_week_ago
    })
    
    # Nếu không có dữ liệu cảm biến nào cho người dùng
    if collection_sensor.count_documents({"user": user, "timestamp": {
        "$gte": start_date,
        "$lte": end_date
    }}) == 0:
        return {
            'message': 'Data or user do not have data in the last week',
            'data': []
        }, 200
    
    df = pd.DataFrame(sensors)

    df["timestamp"] = pd.to_datetime(df["timestamp"], format="%Y-%m-%dT%H:%M:%SZ")
    df["year_month"] = df["timestamp"].dt.to_period("M")
    df["lux"] = pd.to_numeric(df["lux"], errors="coerce")
    df["temperature"] = pd.to_numeric(df["temperature"], errors="coerce")
    df["humidity"] = pd.to_numeric(df["humidity"], errors="coerce")

    monthly_avg = df.groupby("year_month")[["lux", "temperature", "humidity"]].mean().reset_index()

    monthly_avg['month_name'] = monthly_avg['year_month'].dt.strftime('%b')
    monthly_avg['year'] = monthly_avg['year_month'].dt.year

    monthly_avg = monthly_avg.reset_index()

    print(monthly_avg)

    sensor_data_list = [
        SensorDataMonth(
            lux=row["lux"],
            temperature=row["temperature"],
            humidity=row["humidity"],
            month=row["month_name"],
            year = row["year"]
        )
        for index, row in monthly_avg.iterrows()
    ]

    print(sensor_data_list)

    # Convert data to JSON response
    response_data = {
        "total_data": len(sensor_data_list),
        "sensor_data": jsonable_encoder(sensor_data_list)  # Converts objects to JSON-compatible format
    }

    # Return JSON response with status code
    return {
        'message': 'Get all data successfully',
        'data': response_data
    }, 200


def service_get_all_data_week(user: str):
    # Tính thời gian bắt đầu và kết thúc cho khoảng thời gian 1 tuần
    # Go back 12 months from the current date
    start_date = (datetime.now(timezone.utc) - relativedelta(weeks=1)).strftime("%Y-%m-%dT%H:%M:%SZ")

    # Lấy thời gian hiện tại
    end_date = datetime.now(timezone.utc).strftime("%Y-%m-%dT%H:%M:%SZ")

    # Debug thông tin thời gian
    print(f"Fetching data from {start_date} to {end_date} for user: {user}")

    sensors = collection_sensor.find({
        "user": user,
        "timestamp": {
                "$gte": start_date,
                "$lte": end_date
            }  # Lọc dữ liệu có timestamp >= one_week_ago
    })
    
    # Nếu không có dữ liệu cảm biến nào cho người dùng
    if collection_sensor.count_documents({"user": user, "timestamp": {
        "$gte": start_date,
        "$lte": end_date
    }}) == 0:
        return {
            'message': 'Data or user do not have data in the last week',
            'data': []
        }, 200
    
    df = pd.DataFrame(sensors)

    # Chuyển timestamp về dạng datetime
    df["timestamp"] = pd.to_datetime(df["timestamp"], format="%Y-%m-%dT%H:%M:%SZ")

    # Lấy tên thứ trong tuần (Monday, Tuesday, ...)
    df["weekday"] = df["timestamp"].dt.strftime("%A")  

    # Lấy ngày dạng YYYY-MM-DD
    df["date"] = df["timestamp"].dt.date  

    # Chuyển đổi dữ liệu về dạng số
    df["lux"] = pd.to_numeric(df["lux"], errors="coerce")
    df["temperature"] = pd.to_numeric(df["temperature"], errors="coerce")
    df["humidity"] = pd.to_numeric(df["humidity"], errors="coerce")

    # Nhóm theo ngày (date) và thứ (weekday), sau đó tính trung bình
    daily_avg = df.groupby(["date", "weekday"])[["lux", "temperature", "humidity"]].mean().reset_index()

    # In kết quả
    print(daily_avg)

    sensor_data_list = [
        SensorDataWeek(
            lux=row["lux"],
            temperature=row["temperature"],
            humidity=row["humidity"],
            day=row["weekday"]
        )
        for index, row in daily_avg.iterrows()
    ]

    print(sensor_data_list)

    # Convert data to JSON response
    response_data = {
        "total_data": len(sensor_data_list),
        "sensor_data": jsonable_encoder(sensor_data_list)  # Converts objects to JSON-compatible format
    }

    # Return JSON response with status code
    return {
        'message': 'Get all data successfully',
        'data': response_data
    }, 200


def service_get_all_data_day(user: str):
    # Tính thời gian bắt đầu và kết thúc cho khoảng thời gian 1 tuần
    # Go back 12 months from the current date
    start_date = (datetime.now(timezone.utc) - relativedelta(days=1)).strftime("%Y-%m-%dT%H:%M:%SZ")

    # Lấy thời gian hiện tại
    end_date = datetime.now(timezone.utc).strftime("%Y-%m-%dT%H:%M:%SZ")

    # Debug thông tin thời gian
    print(f"Fetching data from {start_date} to {end_date} for user: {user}")

    sensors = collection_sensor.find({
        "user": user,
        "timestamp": {
                "$gte": start_date,
                "$lte": end_date
            }  # Lọc dữ liệu có timestamp >= one_week_ago
    })
    
    # Nếu không có dữ liệu cảm biến nào cho người dùng
    if collection_sensor.count_documents({"user": user, "timestamp": {
        "$gte": start_date,
        "$lte": end_date
    }}) == 0:
        return {
            'message': 'Data or user do not have data in the last week',
            'data': []
        }, 200
    
    df = pd.DataFrame(sensors)

    # Chuyển timestamp về dạng datetime
    df["timestamp"] = pd.to_datetime(df["timestamp"], format="%Y-%m-%dT%H:%M:%SZ") 

    # Lấy ngày dạng YYYY-MM-DD
    df["hour"] = df["timestamp"].dt.hour 

    print(df)

    # Chuyển đổi dữ liệu về dạng số
    df["lux"] = pd.to_numeric(df["lux"], errors="coerce")
    df["temperature"] = pd.to_numeric(df["temperature"], errors="coerce")
    df["humidity"] = pd.to_numeric(df["humidity"], errors="coerce")

    # Nhóm theo ngày (date) và thứ (weekday), sau đó tính trung bình
    daily_avg = df.groupby("hour")[["lux", "temperature", "humidity"]].mean().reset_index()

    # In kết quả
    print(daily_avg)

    sensor_data_list = [
        SensorDataDay(
            lux=row["lux"],
            temperature=row["temperature"],
            humidity=row["humidity"],
            hour=row["hour"]
        )
        for index, row in daily_avg.iterrows()
    ]

    print(sensor_data_list)

    # Convert data to JSON response
    response_data = {
        "total_data": len(sensor_data_list),
        "sensor_data": jsonable_encoder(sensor_data_list)  # Converts objects to JSON-compatible format
    }

    # Return JSON response with status code
    return {
        'message': 'Get all data successfully',
        'data': response_data
    }, 200