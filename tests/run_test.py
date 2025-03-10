import pytest
import os
import sys

def main():
    print("Chạy tests cho controller_signin")
    # Thêm các tham số cần thiết cho pytest
    pytest_args = [
        "-v",                           # Verbose output
        "tests/test_direct_controller.py",    # Đường dẫn đến file test
        "tests/test_controller_signin.py",    # Đường dẫn đến file test
        "--no-header",                  # Không hiển thị header
        "--no-summary",                 # Không hiển thị summary
    ]
    
    # Chạy pytest với các tham số
    exit_code = pytest.main(pytest_args)
    
    return exit_code

if __name__ == "__main__":
    sys.exit(main())