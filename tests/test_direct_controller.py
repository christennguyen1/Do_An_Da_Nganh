import pytest
from unittest.mock import patch, MagicMock
import sys
import os
import json
from fastapi.responses import JSONResponse

# Thêm thư mục gốc của project vào sys.path để import các module
sys.path.insert(0, os.path.abspath(os.path.join(os.path.dirname(__file__), '..')))

# Import controller_signin function từ file controller của bạn
# Giả sử controller_signin được định nghĩa trong module "app.controllers.auth_controller"
from controller.auth_controller import controller_signin  # Điều chỉnh đường dẫn import nếu cần

# Test trực tiếp function controller_signin
@patch("app.controllers.auth_controller.service_user_login")
@patch("app.controllers.auth_controller.create_jwt_token")
@patch("app.controllers.auth_controller.create_refresh_token")
def test_controller_signin_success(mock_refresh_token, mock_access_token, mock_service):
    # Setup mock
    mock_service.return_value = (
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
    mock_access_token.return_value = "test_access_token"
    mock_refresh_token.return_value = "test_refresh_token"
    
    # Input data
    body = {
        "email": "test@example.com",
        "password": "password123"
    }
    
    # Gọi controller
    response = controller_signin(body)
    
    # Kiểm tra response type
    assert isinstance(response, JSONResponse)
    
    # Parse response content
    content = json.loads(response.body.decode('utf-8'))
    
    # Kiểm tra kết quả
    assert response.status_code == 200
    assert content["success"] == True
    assert content["data"]["email"] == "test@example.com"
    assert content["access_token"] == "test_access_token"
    assert content["refresh_token"] == "test_refresh_token"
    
    # Kiểm tra các mock function được gọi đúng cách
    mock_service.assert_called_once_with(body)
    mock_access_token.assert_called_once_with({"sub": "test@example.com"})
    mock_refresh_token.assert_called_once_with({"sub": "test@example.com"})

@patch("app.controllers.auth_controller.service_user_login")
def test_controller_signin_invalid_credentials(mock_service):
    # Setup mock
    mock_service.return_value = (
        {
            "success": False,
            "message": "Invalid credentials"
        },
        401
    )
    
    # Input data
    body = {
        "email": "test@example.com",
        "password": "wrong_password"
    }
    
    # Gọi controller
    response = controller_signin(body)
    
    # Parse response content
    content = json.loads(response.body.decode('utf-8'))
    
    # Kiểm tra kết quả
    assert response.status_code == 401
    assert content["success"] == False
    assert content["access_token"] == ""
    assert content["refresh_token"] == ""

@patch("app.controllers.auth_controller.service_user_login")
def test_controller_signin_exception(mock_service):
    # Setup mock để ném exception
    mock_service.side_effect = Exception("Database error")
    
    # Input data
    body = {
        "email": "test@example.com",
        "password": "password123"
    }
    
    # Gọi controller
    response = controller_signin(body)
    
    # Parse response content
    content = json.loads(response.body.decode('utf-8'))
    
    # Kiểm tra kết quả
    assert response.status_code == 500
    assert content["status"] == 500
    assert content["message"] == "Database error"
    assert content["error"] == 1