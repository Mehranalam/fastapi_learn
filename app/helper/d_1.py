from fastapi import Depends, FastAPI, HTTPException, status, Header
import jwt, os
import sys
from typing import Dict
from datetime import datetime, timedelta
from pydantic import BaseModel
from jwt.exceptions import InvalidTokenError

sys.path.append(os.path.dirname(os.path.abspath(__file__)))
from d_2 import user_collection

JWT_SECRET = os.getenv("JWT_SECRET")
JWT_ALGORITHM = os.getenv("JWT_ALGORITHM")
expiration_time = os.getenv("JWT_EXPIRATION_MINUTES") or 0
JWT_EXPIRATION_MINUTES = int(expiration_time)

async def check_user_is_admin(authorization: str = Header(...)):
    email = await get_email_from_token(authorization)
    user = user_collection.find_one({'email': email})
    if user is None:
        raise HTTPException(detail='User not found', status_code=404)
    if user['user_type'] != 'admin':
        raise HTTPException(detail='User is not Admin', status_code=400)
    return user

async def get_email_from_token(authorization: str = Header(...)):
    try:
        token = authorization.split(" ")[1]
        decode_token = decode_jwt_token(token)
        email = decode_token["sub"]
    except Exception as e:
        print(f"Error-mehran: {str(e)}")
        raise HTTPException(detail="Invalid token", status_code=400)

    return email

def decode_jwt_token(token: str):
    try:
        payload = jwt.decode(token, JWT_SECRET, algorithms=[JWT_ALGORITHM])
        return payload
    except jwt.PyJWTError as e:
        print(f"Error-mehran-data: {str(e)}")
        raise HTTPException(detail="Invalid token", status_code=400)

def encode_jwt_token(email: str):
    payload = {
        "sub": email,
        "exp": datetime.utcnow() + timedelta(minutes=JWT_EXPIRATION_MINUTES)
    }
    token = jwt.encode(payload, JWT_SECRET, algorithm=JWT_ALGORITHM)
    return token

async def get_status_list_from_query(statuses):
    status_list = statuses.split(",")
    lst = []
    for status in status_list:
        lst.append(status.strip())
    return lst
