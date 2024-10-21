
from typing import Optional
from fastapi import FastAPI, Depends
from fastapi import Depends, FastAPI, HTTPException, status
from datetime import datetime
import sys
import os

sys.path.append(os.path.dirname(os.path.abspath(__file__)))
"""When running the files, I encountered the problem of 
(ModuleNotFoundError: No module named 'd_1 & d_2'). 
By adding this line, the problem was solved.
"""
from helper.d_1 import *
from helper.d_2 import *

from tools import create_paginate_response

app = FastAPI()

class LoginRequest(BaseModel):
    email: str
    password: str

@app.post("/login")
async def login(login_request: LoginRequest):
    user = user_collection.find_one({"email": login_request.email})
    if user is None or user['password'] != login_request.password:
        raise HTTPException(status_code=status.HTTP_401_UNAUTHORIZED, detail="Invalid credentials")
    
    token = encode_jwt_token(login_request.email)
    
    return {"access_token": token, "token_type": "bearer"}

@app.get("/payout")
async def all_payout(
    statuses: Optional[str] = None, page: Optional[int] = None, start_date: Optional[datetime] = None,
    end_date: Optional[datetime] = None, user_type: Optional[str] = None,
    payment_start_date:  Optional[datetime] = None, payment_end_date: Optional[datetime] = None,
    admin: str = Depends(check_user_is_admin)
):
    match = {'created': {}, "payment_date": {}}
    
    if start_date:
        match['created']['$gte'] = start_date
    if end_date:
        match['created']['$lte'] = end_date

    if payment_start_date:
        match['payment_date']['$gte'] = payment_start_date
    if payment_end_date:
        match['payment_date']['$lte'] = payment_end_date
    if len(match['created']) == 0:
        del match["created"]
    if len(match["payment_date"]) == 0:
        del match["payment_date"]
    if user_type:
        match['user_type'] = user_type
    if statuses:
        status_list = await get_status_list_from_query(statuses)
        match['status'] = {'$in': status_list}

    return await create_paginate_response(page, payout_collection, match)
