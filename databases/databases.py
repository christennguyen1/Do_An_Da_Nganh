from pymongo import MongoClient
import gridfs
import requests
import sys
from Adafruit_IO import MQTTClient
import os
from dotenv import load_dotenv

# Đường dẫn tuyệt đối hoặc tương đối đến tệp .env bạn muốn sử dụng
env_path = os.path.join('config', '.env')  # Thay 'config' bằng thư mục chứa .env của bạn nếu cần

# Tải tệp .env từ đường dẫn đã chỉ định
load_dotenv(env_path)

# In ra đường dẫn đang được load
print(f"Loading environment variables from: {env_path}")

# Tải các biến môi trường từ tệp .env


#MongoDB
mongodb_uri = os.getenv("MONGO_URI")

client = MongoClient(mongodb_uri)

db = client["db_da_nganh"]

fs = gridfs.GridFS(db)

collection_sensor = db["sensors"]
collection_user = db["users"]
collection_relay = db["relay"]
collection_setup_temperature = db["setup_temperature"]
collection_setup_pir = db["setup_pir"]
collection_setup_light = db["setup_light"]

#Adafruit
ADA_USERNAME = os.getenv("AIO_USERNAME_ADAFRUIT")
ADA_KEY = os.getenv("AIO_KEY_ADAFRUIT_1")
AIO_FEED_ID = ["nutnhan-fan", "nutnhan-door", "nutnhan-light", "nutnhan-pump", "va-tem", "va-lux", "va-pir"]

print(ADA_KEY)

def connected (client) :
    print ("Ket noi thanh cong...")
    for feed in AIO_FEED_ID :
        client.subscribe(feed)


def subscribe ( client , userdata , mid , granted_qos ) :
    print ("Subcribe thanh cong...")

def disconnected ( client ) :
    print ("Ngat ket noi...")
    sys.exit (1)
    
def message ( client , feed_id , payload ):
    print ("Nhan du lieu : " + feed_id + " - " + payload )


client = MQTTClient ( ADA_USERNAME , ADA_KEY )
client.on_connect = connected
client.on_disconnect = disconnected
client.on_message = message
client.on_subscribe = subscribe
client.connect ()
client.loop_background ()


def publish_to_adafruit(feed, value):
    client.publish(feed, value)
