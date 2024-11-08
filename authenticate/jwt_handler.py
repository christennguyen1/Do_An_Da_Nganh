from datetime import datetime, timedelta
from fastapi import HTTPException
import jwt
from jwt import PyJWTError, ExpiredSignatureError
import os

SECRET_KEY = os.getenv("SECRET_KEY")
ALGORITHM = os.getenv("ALGORITHM")
ACCESS_TOKEN_EXPIRE_MINUTES = int(os.getenv("ACCESS_TOKEN_EXPIRE_MINUTES"))

def create_jwt_token(data: dict):
    expiration = datetime.utcnow() + timedelta(minutes=ACCESS_TOKEN_EXPIRE_MINUTES)
    data.update({"exp": expiration})
    return jwt.encode(data, SECRET_KEY, algorithm=ALGORITHM)

def verify_jwt_token(token: str):
    try:
        payload = jwt.decode(token, SECRET_KEY, algorithms=[ALGORITHM])
        username: str = payload.get("sub")
        if username is None:
            raise HTTPException(status_code=401, detail="Invalid token")
        return username
    except ExpiredSignatureError:
        raise HTTPException(status_code=401, detail="Token has expired. Please refresh.")
    except PyJWTError:
        raise HTTPException(status_code=401, detail="Invalid token")
