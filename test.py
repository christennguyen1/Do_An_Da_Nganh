import os
from dotenv import load_dotenv

# Đường dẫn tuyệt đối hoặc tương đối đến tệp .env bạn muốn sử dụng
env_path = os.path.join('config', '.env')  # Thay 'config' bằng thư mục chứa .env của bạn nếu cần

# Tải tệp .env từ đường dẫn đã chỉ định
load_dotenv(env_path)

# In ra đường dẫn đang được load
print(f"Loading environment variables from: {env_path}")

# Kiểm tra một biến môi trường
ADA_USERNAME = os.getenv("AIO_USERNAME_ADAFRUIT")
ADA_KEY = os.getenv("AIO_KEY_ADAFRUIT_1")
print("ADA_USERNAME:", ADA_USERNAME)
print("ADA_KEY:", ADA_KEY)
