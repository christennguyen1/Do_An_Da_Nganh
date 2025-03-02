from fastapi import FastAPI, HTTPException
from pydantic import BaseModel
from fastapi.middleware.cors import CORSMiddleware
import boto3
from typing import List
from dotenv import load_dotenv
import os

env_path = os.path.join('config', '.env')  # Thay 'config' bằng thư mục chứa .env của bạn nếu cần

# Tải tệp .env từ đường dẫn đã chỉ định
load_dotenv(env_path)

AWS_ACCESS_KEY = os.getenv('AWS_ACCESS_SES_KEY')
AWS_SECRET_KEY = os.getenv('AWS_SECRET_SES_KEY')
AWS_REGION = os.getenv('AWS_REGION')


if not all([AWS_ACCESS_KEY, AWS_SECRET_KEY, AWS_REGION]):
    raise ValueError("Missing AWS SES credentials in environment variables.")

app = FastAPI()

app.add_middleware(
    CORSMiddleware,
    allow_origins=[
        "http://localhost:3000",  # React
        "http://localhost:8080",  # Vue.js
        "http://localhost:4200",  # Angular
        "http://127.0.0.1:3000",  # Thêm các phiên bản 127.0.0.1 nếu cần
        "http://127.0.0.1:8080",
        "http://127.0.0.1:4200"
    ],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

ses_client = boto3.client(
    'ses',
    region_name=AWS_REGION,
    aws_access_key_id=AWS_ACCESS_KEY,
    aws_secret_access_key=AWS_SECRET_KEY
)

class EmailContent(BaseModel):
    EmailAddresses: List[str]  # Đã sửa lỗi chính tả
    message: str = "Hello, this is a test message"

@app.post("/sendMessage")
async def send_message(email_content: EmailContent):
    try:
        response = ses_client.send_email(
            Source='vinh.nguyen123@hcmut.edu.vn',
            Destination={
                'ToAddresses': email_content.EmailAddresses
            },
            Message={
                'Subject': {'Data': 'Test Email from FastAPI'},
                'Body': {'Text': {'Data': email_content.message}}
            }
        )
        return {"Message": "Email Sent", "Response": response}
    except Exception as e:
        raise HTTPException(status_code=400, detail=f"An error occurred: {str(e)}")

@app.post("/verifyEmailAddresses")
async def verify_email_addresses(email_content: EmailContent):
    try:
        responses = []
        for email in email_content.EmailAddresses:
            response = ses_client.verify_email_address(EmailAddress=email)
            responses.append(response)
        return {
            "Message": "Verification mail sent",
            "Response": responses
        }
    except Exception as e:
        raise HTTPException(status_code=400, detail=f"An error occurred: {str(e)}")
