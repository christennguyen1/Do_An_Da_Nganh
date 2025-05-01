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
    
    temperature = float(data.get('temperature', 0))
    humidity_soil = float(data.get('humidity_soil', 0))
    lux = float(data.get('lux', 0))
    N_soil = float(data.get('N_soil', 0))
    P_soil = float(data.get('P_soil', 0))
    K_soil = float(data.get('K_soil', 0))
    
    # Lấy user_id hoặc sử dụng giá trị mặc định
    user_id = data.get('user_id', 1)  # Mặc định là user_id = 1 nếu không có
    
    vietnam_tz = pytz.timezone('Asia/Ho_Chi_Minh')
    vietnam_time = datetime.now(vietnam_tz)
    
    formatted_time = vietnam_time.strftime("%Y-%m-%dT%H:%M:%S")
    print(f"Thời gian nhận dữ liệu: {formatted_time}")
    
    # Chuẩn bị dữ liệu cảm biến
    sensor_data = {
        'temperature': temperature,
        'humidity_soil': humidity_soil,
        'lux': lux,
        'N_soil': N_soil,
        'P_soil' : P_soil,
        'K_soil' : K_soil,
        'timestamp': formatted_time
    }
    
    collection_sensor_data.insert_one(sensor_data)
    
    # Trả về thông tin sau khi xử lý
    response = {
        'message': 'Data sensors post successfully',
        'data': {
            'temperature': sensor_data['temperature'],
            'humidity_soil': sensor_data['humidity_soil'],
            'lux': sensor_data['lux'],
            'N_soil': sensor_data['N_soil'],
            'P_soil': sensor_data['P_soil'],
            'K_soil': sensor_data['N_soil'],
            'timestamp': formatted_time
        }
    }
    
    return response, 201


def service_get_all_data(user: str):
    # Tìm bản ghi có timestamp lớn nhất
    latest_sensor = collection_sensor_data.find_one(
        {},  # Không có điều kiện lọc
        sort=[("timestamp", -1)]  # Sắp xếp giảm dần theo timestamp
    )
    
    # Nếu không có dữ liệu cảm biến nào cho người dùng
    if latest_sensor is None:
        return {
            'message': 'Data or user do not have any data',
            'data': []
        }, 200
    
    # Tạo danh sách dữ liệu cảm biến với bản ghi mới nhất
    sensor_data_list = [
        SensorData(
            lux=latest_sensor["lux"],
            temperature=latest_sensor["temperature"],
            humidity=latest_sensor["humidity"],
            soil=latest_sensor["soil"],
            timestamp=latest_sensor["timestamp"]
        )
    ]
    
    # Chuyển đổi dữ liệu thành JSON
    response_data = {
        "total_data": len(sensor_data_list),
        "sensor_data": jsonable_encoder(sensor_data_list)  # Chuyển dữ liệu thành JSON
    }
    
    # Trả về dữ liệu JSON
    return {
        'message': 'Get latest data successfully',
        'data': response_data
    }, 200


def service_get_all_data_month(user: str):
    # Sử dụng múi giờ Việt Nam (UTC+7)
    vietnam_tz = timezone(timedelta(hours=7))
    
    # Tính thời gian cho khoảng 12 tháng trước đến hiện tại theo giờ Việt Nam
    end_date = datetime.now(vietnam_tz)
    start_date = end_date - relativedelta(months=12)
    
    # Chuyển sang chuỗi ISO format để so sánh với dữ liệu trong MongoDB
    start_date_str = start_date.strftime("%Y-%m-%dT%H:%M:%S")
    end_date_str = end_date.strftime("%Y-%m-%dT%H:%M:%S")
    
    # Log thông tin debug
    print(f"Fetching data from {start_date_str} to {end_date_str} for user: {user}")
    
    # Truy vấn dữ liệu trong khoảng thời gian
    query = {
        "timestamp": {
            "$gte": start_date_str,
            "$lte": end_date_str
        }
    }
    
    # Thêm điều kiện user nếu cần
    if user:
        query["user"] = user
    
    # Kiểm tra số lượng documents trước khi truy vấn đầy đủ
    count = collection_sensor_data.count_documents(query)
    
    if count == 0:
        return {
            'message': 'No data available for the last 12 months',
            'data': []
        }, 200
    
    # Truy vấn dữ liệu
    sensors_data = list(collection_sensor_data.find(query))
    
    # Chuyển đổi sang DataFrame
    df = pd.DataFrame(sensors_data)
    
    # Chuyển đổi timestamp từ chuỗi sang datetime và chỉ định múi giờ Việt Nam
    df["timestamp"] = pd.to_datetime(df["timestamp"])
    
    # Đảm bảo timestamp được xử lý theo múi giờ Việt Nam
    if df["timestamp"].dt.tz is None:
        df["timestamp"] = df["timestamp"].dt.tz_localize(vietnam_tz)
    else:
        df["timestamp"] = df["timestamp"].dt.tz_convert(vietnam_tz)
    
    # Tạo cột year_month từ timestamp
    df["year_month"] = df["timestamp"].dt.to_period("M")
    
    # Đảm bảo các cột dữ liệu cảm biến là số
    numeric_columns = ["lux", "temperature", "humidity", "soil"]
    for col in numeric_columns:
        if col in df.columns:
            df[col] = pd.to_numeric(df[col], errors="coerce")
        else:
            df[col] = None
    
    # Nhóm theo tháng và tính trung bình
    monthly_avg = df.groupby("year_month")[numeric_columns].mean().reset_index()
    
    # Thêm cột month_name và year
    monthly_avg['month_name'] = monthly_avg['year_month'].dt.strftime('%b')
    monthly_avg['year'] = monthly_avg['year_month'].dt.year
    
    # Tạo danh sách dữ liệu theo tháng
    sensor_data_list = []
    
    for _, row in monthly_avg.iterrows():
        # Xử lý nếu có cột soil thiếu
        soil_value = row.get("soil", None)
        
        sensor_data_list.append(
            SensorDataMonth(
                lux=row["lux"],
                temperature=row["temperature"],
                humidity=row["humidity"],
                soil=soil_value,
                month=row["month_name"],
                year=row["year"]
            )
        )
    
    # Debug: in kết quả
    print(f"Found data for {len(sensor_data_list)} months")
    
    # Chuyển đổi thành JSON để trả về
    response_data = {
        "total_data": len(sensor_data_list),
        "sensor_data": jsonable_encoder(sensor_data_list)
    }
    
    return {
        'message': 'Monthly average data retrieved successfully',
        'data': response_data
    }, 200


def service_get_all_data_week(user: str):
    # Sử dụng múi giờ Việt Nam (UTC+7)
    vietnam_tz = timezone(timedelta(hours=7))
    
    # Tính thời gian cho khoảng 1 tuần trước đến hiện tại theo giờ Việt Nam
    end_date = datetime.now(vietnam_tz)
    start_date = end_date - relativedelta(weeks=1)
    
    # Chuyển sang chuỗi ISO format để so sánh với dữ liệu trong MongoDB
    start_date_str = start_date.strftime("%Y-%m-%dT%H:%M:%S")
    end_date_str = end_date.strftime("%Y-%m-%dT%H:%M:%S")
    
    # Log thông tin debug
    print(f"Fetching data from {start_date_str} to {end_date_str} for user: {user}")
    
    # Truy vấn dữ liệu trong khoảng thời gian
    query = {
        "timestamp": {
            "$gte": start_date_str,
            "$lte": end_date_str
        }
    }
    
    # Thêm điều kiện user nếu cần
    if user:
        query["user"] = user
    
    # Kiểm tra số lượng documents trước khi truy vấn đầy đủ
    count = collection_sensor_data.count_documents(query)
    
    if count == 0:
        return {
            'message': 'No data available for the last week',
            'data': []
        }, 200
    
    # Truy vấn dữ liệu
    sensors_data = list(collection_sensor_data.find(query))
    
    # Chuyển đổi sang DataFrame
    df = pd.DataFrame(sensors_data)
    
    # Chuyển đổi timestamp từ chuỗi sang datetime và chỉ định múi giờ Việt Nam
    df["timestamp"] = pd.to_datetime(df["timestamp"])
    
    # Đảm bảo timestamp được xử lý theo múi giờ Việt Nam
    if df["timestamp"].dt.tz is None:
        df["timestamp"] = df["timestamp"].dt.tz_localize(vietnam_tz)
    else:
        df["timestamp"] = df["timestamp"].dt.tz_convert(vietnam_tz)
    
    # Lấy tên thứ trong tuần (tiếng Việt)
    weekday_map = {
        0: "Thứ Hai",
        1: "Thứ Ba",
        2: "Thứ Tư", 
        3: "Thứ Năm",
        4: "Thứ Sáu",
        5: "Thứ Bảy",
        6: "Chủ Nhật"
    }
    df["weekday_num"] = df["timestamp"].dt.weekday
    df["weekday"] = df["weekday_num"].map(weekday_map)
    
    # Lấy ngày dạng YYYY-MM-DD
    df["date"] = df["timestamp"].dt.date
    
    # Đảm bảo các cột dữ liệu cảm biến là số
    numeric_columns = ["lux", "temperature", "humidity", "soil"]
    for col in numeric_columns:
        if col in df.columns:
            df[col] = pd.to_numeric(df[col], errors="coerce")
        else:
            df[col] = None
    
    # Nhóm theo ngày và thứ, sau đó tính trung bình
    daily_avg = df.groupby(["date", "weekday", "weekday_num"])[numeric_columns].mean().reset_index()
    
    # Sắp xếp theo thứ trong tuần để hiển thị đúng thứ tự
    daily_avg = daily_avg.sort_values("weekday_num")
    
    # Tạo danh sách dữ liệu theo ngày trong tuần
    sensor_data_list = []
    
    for _, row in daily_avg.iterrows():
        # Xử lý nếu có cột soil thiếu
        soil_value = row.get("soil", None)
        
        sensor_data_list.append(
            SensorDataWeek(
                lux=row["lux"],
                temperature=row["temperature"],
                humidity=row["humidity"],
                soil=soil_value,
                day=row["weekday"]
            )
        )
    
    # Debug: in kết quả
    print(f"Found data for {len(sensor_data_list)} days")
    
    # Chuyển đổi thành JSON để trả về
    response_data = {
        "total_data": len(sensor_data_list),
        "sensor_data": jsonable_encoder(sensor_data_list)
    }
    
    return {
        'message': 'Weekly average data retrieved successfully',
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