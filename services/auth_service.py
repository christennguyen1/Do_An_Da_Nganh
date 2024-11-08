from pydantic import BaseModel
import jwt
from jwt import PyJWTError, ExpiredSignatureError
from authenticate.jwt_handler import verify_jwt_token, create_jwt_token, SECRET_KEY, ALGORITHM
from fastapi import HTTPException
from pydantic import BaseModel
import asyncio


fake_users_db = {
    "testuser": {
        "username": "testuser",
        "password": "testpassword"
    }
}

def authenticate_user(username: str, password: str):
    user = fake_users_db.get(username)
    if user and user["password"] == password:
        return True
    return False

def refresh_user_token(token: str):
    try:
        payload = jwt.decode(token, SECRET_KEY, algorithms=[ALGORITHM], options={"verify_exp": False})
        username: str = payload.get("sub")
        if username is None:
            raise HTTPException(status_code=401, detail="Invalid token")

        new_token = create_jwt_token({"sub": username})
        return {"token": new_token, "token_type": "Bearer"}
    except PyJWTError:
        raise HTTPException(status_code=401, detail="Invalid token")
