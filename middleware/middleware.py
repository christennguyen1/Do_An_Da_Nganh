from fastapi.security import OAuth2PasswordBearer
from passlib.context import CryptContext
import asyncio
from databases.databases import *
import httpx
import os


class Password:
    def __init__(self):
        pwd_context = CryptContext(schemes=["bcrypt"], deprecated="auto")
        oauth2_scheme = OAuth2PasswordBearer(tokenUrl="token")


    def hash_password(self, password: str) -> str:
        return self.pwd_context.hash(password)


    def verify_password(self, plain_password: str, hashed_password: str) -> str:
        return self.pwd_context.verify(plain_password, hashed_password)
    

# Hàm lấy dữ liệu từ feed cụ thể
async def get_data_from_feed(feed_key: str):
    url = f"https://io.adafruit.com/api/v2/{ADA_USERNAME}/feeds/{feed_key}/data"
    headers = {"X-AIO-Key": ADA_KEY}
    async with httpx.AsyncClient() as client:
        response = await client.get(url)
        response.raise_for_status()
        return response.json()

def get_max_timestamp_from_mongo():
    max_record = collection_sensor.find_one({}, sort=[("timestamp", -1)])
    return max_record["timestamp"] if max_record else None

async def save_data_to_mongo(data):
    res = []
    for value in data:
        user, temperature, humidity, lux = value['value'].split('_')
        timestamp = value['created_at']
        data_json = {
            "user": user,
            "temperature": temperature,
            "humidity": humidity,
            "lux": lux,
            "timestamp": timestamp
        }
        res.append(data_json)
    if res:
        collection_sensor.insert_many(res)

async def periodic_data_collection():
    while True:
        try:
            feed_keys = ["sensors"]
            all_data = []
            max_timestamp = get_max_timestamp_from_mongo()

            if max_timestamp is None:
                print("No records found in MongoDB. Fetching all data from Adafruit.")
                # Nếu không có dữ liệu trong MongoDB, lấy toàn bộ dữ liệu từ Adafruit
                for feed_key in feed_keys:
                    feed_data = await get_data_from_feed(feed_key)
                    all_data.extend(feed_data)
            else:
                for feed_key in feed_keys:
                    feed_data = await get_data_from_feed(feed_key)
                    new_data = [value for value in feed_data if value['created_at'] > max_timestamp]
                    all_data.extend(new_data)

            if all_data:
                await save_data_to_mongo(all_data)
                print(f"Collected and saved new data: {len(all_data)} records.")
            else:
                print("No new data to save.")

        except Exception as e:
            print(f"An error occurred: {str(e)}")

        await asyncio.sleep(1200)  # Đợi 20 phút
