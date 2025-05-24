from fastapi import HTTPException
from fastapi.encoders import jsonable_encoder  # Thêm thư viện này
from databases.databases import *
from schemas import SensorData, SensorDataWeek, SensorDataDay, SensorDataMonth
import asyncio
from datetime import datetime, timedelta, timezone
import pandas as pd
from dateutil.relativedelta import relativedelta
import pytz
from services.data_analysis_service import handle_sensor_data, detect_anomalies

async def service_post_all_data(body):
    data = body
    
    device_name = str(data.get('device_name', ""))
    aqi = float(data.get('aqi', 0))
    no2Aqi = float(data.get('no2Aqi', 0))
    so2Aqi = float(data.get('so2Aqi', 0))
    o3Aqi = float(data.get('o3Aqi', 0))
    pm25Aqi = float(data.get('pm25Aqi', 0))
    pm10Aqi = float(data.get('pm10Aqi', 0))
    coAqi = float(data.get('coAqi', 0))
    
    vietnam_tz = pytz.timezone('Asia/Ho_Chi_Minh')
    vietnam_time = datetime.now(vietnam_tz)
    
    formatted_time = vietnam_time.strftime("%Y-%m-%dT%H:%M:%S")
    print(f"Thời gian nhận dữ liệu: {formatted_time}")

    
    # URL và timeout chung
    login_url = "http://123.25.190.46:8081/v1/login"
    air_quality_url = "http://123.25.190.46:8081/v1/air-quality"
    timeout = 60

    # Login để lấy token
    try:
        login_headers = {"Content-Type": "application/json"}
        login_payload = {"username": "user", "password": "password123"}
        login_response = requests.post(login_url, json=login_payload, headers=login_headers, timeout=timeout)
        login_response.raise_for_status()
        token = login_response.json()["token"]
        print("Login thành công")
    except Exception as e:
        print(f"Lỗi login: {e}")
        return

    # Gửi air quality
    air_quality_headers = {
        "Content-Type": "application/json",
        "Authorization": f"Bearer {token}"
    }
    air_quality_payload = {
        "device_name": device_name,
        "aqi": aqi,
        "no2Aqi": no2Aqi,
        "so2Aqi": so2Aqi,
        "o3Aqi": o3Aqi,
        "pm25Aqi": pm25Aqi,
        "pm10Aqi": pm10Aqi,
        "coAqi": coAqi,
        "timestamp": str(formatted_time)
    }

    try:
        air_quality_response = requests.post(air_quality_url, json=air_quality_payload, headers=air_quality_headers, timeout=timeout)
        air_quality_response.raise_for_status()
        print("Gửi air quality thành công:", air_quality_response.json())
    except requests.exceptions.HTTPError as e:
        if air_quality_response.status_code in (401, 403):  # Lỗi xác thực
            print(f"Lỗi xác thực: {e}, thử login lại")
            try:
                # Login lại để lấy token mới
                login_response = requests.post(login_url, json=login_payload, headers=login_headers, timeout=timeout)
                login_response.raise_for_status()
                token = login_response.json()["token"]
                print("Login lại thành công")
                
                # Gửi lại air quality với token mới
                air_quality_headers["Authorization"] = f"Bearer {token}"
                air_quality_response = requests.post(air_quality_url, json=air_quality_payload, headers=air_quality_headers, timeout=timeout)
                air_quality_response.raise_for_status()
                print("Gửi air quality thành công:", air_quality_response.json())
            except Exception as retry_e:
                print(f"Lỗi khi thử lại: {retry_e}")
        else:
            print(f"Lỗi HTTP: {e}")
    except Exception as e:
        print(f"Lỗi gửi air quality: {e}")
    
    # Trả về thông tin sau khi xử lý
    response = {
        'message': 'Data sensors post successfully',
        'data': air_quality_payload
    }
    
    return response, 201


def service_get_all_data(user: str):
    # Tính thời gian bắt đầu và kết thúc cho khoảng thời gian 1 tuần
    start_date = (datetime.now(timezone.utc) - timedelta(weeks=1)).strftime("%Y-%m-%dT%H:%M:%SZ")

    # Lấy thời gian hiện tại
    end_date = datetime.now(timezone.utc).strftime("%Y-%m-%dT%H:%M:%SZ")

    # Debug thông tin thời gian
    print(f"Fetching data from {start_date} to {end_date} for user: {user}")

    sensors = collection_sensor_data.find({
        "timestamp": {
                # "$gte": start_date,
                "$lte": end_date
            }  # Lọc dữ liệu có timestamp >= one_week_ago
    })
    
    # Nếu không có dữ liệu cảm biến nào cho người dùng
    if collection_sensor_data.count_documents({ "timestamp": {
        # "$gte": start_date,
        "$lte": end_date
    }}) == 0:
        return {
            'message': 'Data or user do not have data in the last week',
            'data': []
        }, 200
    
    print(sensors[0])

    # Tạo danh sách dữ liệu cảm biến
    sensor_data_list = [
        SensorData(
            lux=sensors[0]["lux"], 
            temperature=sensors[0]["temperature"], 
            humidity_soil=sensors[0]["humidity_soil"], 
            N_soil=sensors[0]["N_soil"],
            P_soil=sensors[0]["P_soil"],
            K_soil=sensors[0]["K_soil"],
            timestamp=sensors[0]["timestamp"]  # Đảm bảo timestamp theo định dạng mong muốn
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

    sensors = collection_sensor_data.find({
        "timestamp": {
                "$gte": start_date,
                "$lte": end_date
            }  # Lọc dữ liệu có timestamp >= one_week_ago
    })
    
    # Nếu không có dữ liệu cảm biến nào cho người dùng
    if collection_sensor_data.count_documents({"timestamp": {
        "$gte": start_date,
        "$lte": end_date
    }}) == 0:
        return {
            'message': 'Data or user do not have data in the last week',
            'data': []
        }, 200
    
    df = pd.DataFrame(sensors)

    df["timestamp"] = pd.to_datetime(df["timestamp"], format="%Y-%m-%dT%H:%M:%S")
    df["year_month"] = df["timestamp"].dt.to_period("M")
    df["lux"] = pd.to_numeric(df["lux"], errors="coerce")
    df["temperature"] = pd.to_numeric(df["temperature"], errors="coerce")
    df["humidity_soil"] = pd.to_numeric(df["humidity_soil"], errors="coerce")

    df["N_soil"] = pd.to_numeric(df["N_soil"], errors="coerce")
    df["P_soil"] = pd.to_numeric(df["P_soil"], errors="coerce")
    df["K_soil"] = pd.to_numeric(df["K_soil"], errors="coerce")

    monthly_avg = df.groupby("year_month")[["lux", "temperature", "humidity_soil", "N_soil","P_soil","K_soil"]].mean().reset_index()

    monthly_avg['month_name'] = monthly_avg['year_month'].dt.strftime('%b')
    monthly_avg['year'] = monthly_avg['year_month'].dt.year

    monthly_avg = monthly_avg.reset_index()

    print(monthly_avg)

    sensor_data_list = [
        SensorDataMonth(
            lux=row["lux"],
            temperature=row["temperature"],
            humidity_soil=row["humidity_soil"],
            N_soil=row["N_soil"],
            P_soil=row["P_soil"],
            K_soil=row["K_soil"],
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
    start_date = (datetime.now(timezone.utc) - relativedelta(weeks=1)).strftime("%Y-%m-%dT%H:%M:%S")

    # Lấy thời gian hiện tại
    end_date = datetime.now(timezone.utc).strftime("%Y-%m-%dT%H:%M:%S")

    # Debug thông tin thời gian
    print(f"Fetching data from {start_date} to {end_date} for user: {user}")

    sensors = collection_sensor_data.find({
        "timestamp": {
                "$gte": start_date,
                "$lte": end_date
            }  # Lọc dữ liệu có timestamp >= one_week_ago
    })
    
    # Nếu không có dữ liệu cảm biến nào cho người dùng
    if collection_sensor_data.count_documents({"timestamp": {
        "$gte": start_date,
        "$lte": end_date
    }}) == 0:
        return {
            'message': 'Data or user do not have data in the last week',
            'data': []
        }, 200
    
    df = pd.DataFrame(sensors)

    # Chuyển timestamp về dạng datetime
    df["timestamp"] = pd.to_datetime(df["timestamp"], format="%Y-%m-%dT%H:%M:%S")

    # Lấy tên thứ trong tuần (Monday, Tuesday, ...)
    df["weekday"] = df["timestamp"].dt.strftime("%A")  

    # Lấy ngày dạng YYYY-MM-DD
    df["date"] = df["timestamp"].dt.date  

    # Chuyển đổi dữ liệu về dạng số
    df["lux"] = pd.to_numeric(df["lux"], errors="coerce")
    df["temperature"] = pd.to_numeric(df["temperature"], errors="coerce")
    df["humidity_soil"] = pd.to_numeric(df["humidity_soil"], errors="coerce")

    df["N_soil"] = pd.to_numeric(df["N_soil"], errors="coerce")
    df["P_soil"] = pd.to_numeric(df["P_soil"], errors="coerce")
    df["K_soil"] = pd.to_numeric(df["K_soil"], errors="coerce")

    # Nhóm theo ngày (date) và thứ (weekday), sau đó tính trung bình
    daily_avg = df.groupby(["date", "weekday"])[["lux", "temperature", "humidity_soil", "N_soil", "P_soil" , "K_soil"]].mean().reset_index()

    # In kết quả
    print(daily_avg)

    sensor_data_list = [
        SensorDataWeek(
            lux=row["lux"],
            temperature=row["temperature"],
            humidity_soil=row["humidity_soil"],
            N_soil=row["N_soil"],
            P_soil=row["P_soil"],
            K_soil=row["K_soil"],
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
    vietnam_tz = timezone(timedelta(hours=7))
    
    end_date = datetime.now(vietnam_tz)
    start_date = end_date - relativedelta(days=1)
    
    start_date_str = start_date.strftime("%Y-%m-%dT%H:%M:%S")
    end_date_str = end_date.strftime("%Y-%m-%dT%H:%M:%S")

    print(f"Fetching data from {start_date_str} to {end_date_str} for user: {user}")

    query = {
        "timestamp": {
            "$gte": start_date_str,
            "$lte": end_date_str
        }
    }
    
    count = collection_sensor_data.count_documents(query)
    
    if count == 0:
        return {
            'message': 'No data available for the last 24 hours',
            'data': []
        }, 200
    
    sensors_data = list(collection_sensor_data.find(query))
    
    df = pd.DataFrame(sensors_data)
    
    df["timestamp"] = pd.to_datetime(df["timestamp"])
    
    if df["timestamp"].dt.tz is None:
        df["timestamp"] = df["timestamp"].dt.tz_localize(vietnam_tz)
    else:
        df["timestamp"] = df["timestamp"].dt.tz_convert(vietnam_tz)
    
    df["hour"] = df["timestamp"].dt.hour
    
    # Đảm bảo các cột dữ liệu cảm biến là số
    numeric_columns = ["lux", "temperature", "humidity", "soil"]
    for col in numeric_columns:
        df[col] = pd.to_numeric(df[col], errors="coerce")
    
    # Nhóm theo giờ và tính trung bình
    hourly_avg = df.groupby("hour")[numeric_columns].mean().reset_index()
    
    # Tạo danh sách dữ liệu theo giờ
    sensor_data_list = []
    
    for _, row in hourly_avg.iterrows():
        # Chỉ thêm vào danh sách nếu có dữ liệu cho giờ đó
        if not all(pd.isna(row[col]) for col in numeric_columns):
            sensor_data_list.append(
                SensorDataDay(
                    lux=row["lux"],
                    temperature=row["temperature"],
                    humidity=row["humidity"],
                    soil=row["soil"],
                    hour=int(row["hour"])
                )
            )
    
    # Debug: in kết quả
    print(f"Found data for {len(sensor_data_list)} hours")
    
    # Chuyển đổi thành JSON để trả về
    response_data = {
        "total_data": len(sensor_data_list),
        "sensor_data": jsonable_encoder(sensor_data_list)
    }
    
    return {
        'message': 'Hourly average data retrieved successfully',
        'data': response_data
    }, 200