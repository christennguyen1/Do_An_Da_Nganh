import pytest
import sys
import os
import json
from unittest.mock import patch, MagicMock
from fastapi.testclient import TestClient
from fastapi import FastAPI

# Thêm thư mục gốc của project vào sys.path để import các module
sys.path.insert(0, os.path.abspath(os.path.join(os.path.dirname(__file__), '..')))

# Import controller_signin function từ file controller của bạn
# Giả sử controller_signin được định nghĩa trong module "app.controllers.auth_controller"
from controller.auth_controller import controller_signin  # Điều chỉnh đường dẫn import nếu cần

# Tạo mock app để test
app = FastAPI()

@app.post("/signin")
async def signin_endpoint(body: dict):
    return controller_signin(body)

client = TestClient(app)

# Mock cho service_user_login
@pytest.fixture
def mock_service_user_login():
    with patch("controller.auth_controller.controller_signin") as mock_service:
        yield mock_service

# Mock cho create_jwt_token
@pytest.fixture
def mock_create_jwt_token():
    with patch("authenticate.jwt_handler.create_jwt_token") as mock_token:
        mock_token.return_value = "mocked_access_token"
        yield mock_token

# Mock cho create_refresh_token
@pytest.fixture
def mock_create_refresh_token():
    with patch("authenticate.jwt_handler.create_refresh_token") as mock_token:
        mock_token.return_value = "mocked_refresh_token"
        yield mock_token

# Test đăng nhập thành công
def test_signin_success(mock_service_user_login, mock_create_jwt_token, mock_create_refresh_token):
    # Setup mock response cho service_user_login
    mock_service_user_login.return_value = (
        {
            "success": True,
            "data": {
                "email": "test@example.com",
                "name": "Test User",
                "_id": "60d5ec9af682d67e7d9bd4ab"
            }
        },
        200
    )
    
    # Gọi API endpoint
    response = client.post(
        "/signin",
        json={"email": "test@example.com", "password": "password123"}
    )
    
    # Kiểm tra kết quả
    assert response.status_code == 200
    response_data = response.json()
    assert response_data["success"] == True
    assert response_data["data"]["email"] == "test@example.com"
    assert response_data["access_token"] == "mocked_access_token"
    assert response_data["refresh_token"] == "mocked_refresh_token"
    
    # Kiểm tra xem service_user_login được gọi với đúng tham số
    mock_service_user_login.assert_called_once()
    
    # Kiểm tra xem create_jwt_token và create_refresh_token được gọi với đúng tham số
    mock_create_jwt_token.assert_called_once_with({"sub": "test@example.com"})
    mock_create_refresh_token.assert_called_once_with({"sub": "test@example.com"})

# Test đăng nhập thất bại do thông tin không hợp lệ
def test_signin_invalid_credentials(mock_service_user_login):
    # Setup mock response cho service_user_login
    mock_service_user_login.return_value = (
        {
            "success": False,
            "message": "Invalid credentials"
        },
        401
    )
    
    # Gọi API endpoint
    response = client.post(
        "/signin",
        json={"email": "test@example.com", "password": "wrong_password"}
    )
    
    # Kiểm tra kết quả
    assert response.status_code == 401
    response_data = response.json()
    assert response_data["success"] == False
    assert response_data["access_token"] == ""
    assert response_data["refresh_token"] == ""

# Test đăng nhập thất bại do user không tồn tại
def test_signin_user_not_found(mock_service_user_login):
    # Setup mock response cho service_user_login
    mock_service_user_login.return_value = (
        {
            "success": False,
            "message": "User not found"
        },
        404
    )
    
    # Gọi API endpoint
    response = client.post(
        "/signin",
        json={"email": "nonexistent@example.com", "password": "password123"}
    )
    
    # Kiểm tra kết quả
    assert response.status_code == 404
    response_data = response.json()
    assert response_data["success"] == False
    assert response_data["access_token"] == ""
    assert response_data["refresh_token"] == ""

# Test xử lý exception
def test_signin_exception(mock_service_user_login):
    # Setup mock để ném exception
    mock_service_user_login.side_effect = Exception("Database error")
    
    # Gọi API endpoint
    response = client.post(
        "/signin",
        json={"email": "test@example.com", "password": "password123"}
    )
    
    # Kiểm tra kết quả
    assert response.status_code == 500
    response_data = response.json()
    assert "error" in response_data
    assert response_data["message"] == "Database error"