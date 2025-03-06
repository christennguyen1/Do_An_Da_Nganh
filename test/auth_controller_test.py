import sys
import os
sys.path.insert(0, os.path.abspath(os.path.join(os.path.dirname(__file__), '..')))

import pytest
from unittest.mock import patch
from controller.auth_controller import controller_signin


@pytest.fixture
def mock_body():
    return {"email": "test@example.com", "password": "testpassword"}

@patch("services.user_services.service_user_login")
@patch("authenticate.jwt_handler.create_jwt_token")
@patch("authenticate.jwt_handler.create_refresh_token")
def test_controller_signin_success(mock_create_refresh_token, mock_create_jwt_token, mock_service_user_login, mock_body):
    # Giả lập dữ liệu trả về từ `service_user_login`
    mock_service_user_login.return_value = ({"success": True, "data": {"email": "test@example.com"}}, 200)
    
    # Giả lập JWT token
    mock_create_jwt_token.return_value = "mock_access_token"
    mock_create_refresh_token.return_value = "mock_refresh_token"
    
    response = controller_signin(mock_body)
    
    assert response.status_code == 200
    assert response.json() == {
        "success": True,
        "data": {"email": "test@example.com"},
        "refresh_token": "mock_refresh_token",
        "access_token": "mock_access_token"
    }

def test_controller_signin_failure(mock_body):
    response = controller_signin({})
    assert response[1] == 500
    assert response[0]["status"] == 500
    assert "error" in response[0]
