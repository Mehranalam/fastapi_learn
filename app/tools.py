DEFAULT_PAGE_SIZE = 3
import datetime
from typing import List, Optional
from fastapi import HTTPException
from pymongo.cursor import Cursor
from bson.objectid import ObjectId
import sys
import os

sys.path.append(os.path.dirname(os.path.abspath(__file__)))
from helper.d_2 import wallet_collection

async def check_is_valid_objectId(id: str) -> ObjectId:
    try:
        return ObjectId(id)
    except Exception:
        raise HTTPException(detail="Not valid ObjectId", status_code=400)

async def create_paginate_response(page: Optional[int], collection, match: dict, add_wallet: bool = False) -> dict:
    page, total_docs, result = await paginate_results(page, collection, match, add_wallet)
    return {
        "page": page,
        "pageSize": DEFAULT_PAGE_SIZE,
        "totalPages": -(-total_docs // DEFAULT_PAGE_SIZE) if page else 1,
        "totalDocs": total_docs if page else len(result),
        "results": result,
    }

async def paginate_results(page: Optional[int], collection, match: dict, add_wallet: bool = False) -> tuple:
    total_docs = 0
    if page is None:
        cursor = collection.find(match)
        result = list(cursor)
        result = await process_documents(result, add_wallet)
    else:
        total_docs = collection.count_documents(match)
        if page < 1:
            page = 1

        skip = (page - 1) * DEFAULT_PAGE_SIZE
        limit = DEFAULT_PAGE_SIZE
        cursor = collection.find(match)
        result = await paginate_documents(cursor, skip, limit, add_wallet)
    
    return page, total_docs, result

async def process_documents(docs: List[dict], add_wallet: bool) -> List[dict]:
    for index, doc in enumerate(docs):
        doc["_id"] = str(doc["_id"])
        if "affiliate_tracking_id" in doc:
            doc["affiliate_tracking_id"] = str(doc["affiliate_tracking_id"])
        if "user_id" in doc:
            doc["user_id"] = str(doc["user_id"])

        if add_wallet:
            available_balance, pending_balance = await check_available_balance(doc["_id"])
            doc["available_balance"] = available_balance
            doc["pending_balance"] = pending_balance

        docs[index] = await convert_dict_camel_case(doc)
    return docs

async def check_available_balance(user_id: str) -> tuple:
    user_id = await check_is_valid_objectId(user_id)
    wallet = wallet_collection.find_one({"user_id": user_id})

    if wallet is None:
        raise HTTPException(detail="Wallet not found", status_code=404)

    available_balance = wallet['available_balance']
    pending_balance = 0
    transactions_to_delete = []

    for transaction in wallet["transactions"]:
        if transaction["date_available"] <= datetime.datetime.now():
            available_balance += transaction["amount"]
            transactions_to_delete.append(transaction["id"])
        else:
            pending_balance += transaction["amount"]

    # Update the wallet with the new balances
    wallet_collection.update_one(
        {"user_id": user_id},
        {
            "$set": {
                "available_balance": available_balance,
                "pending_balance": pending_balance,
            },
            "$pull": {
                "transactions": {"id": {"$in": transactions_to_delete}}
            },
        },
    )
    return available_balance, pending_balance

async def snake_to_camel(snake_str: str) -> str:
    components = snake_str.split("_")
    return components[0] + "".join(x.title() for x in components[1:])

async def convert_dict_camel_case(data: dict) -> dict:
    camel_dict = {}
    for key, value in data.items():
        camel_key = await snake_to_camel(key)
        camel_dict[camel_key] = value
    return camel_dict

async def paginate_documents(
    cursor: Cursor, skip: int = 0, limit: int = DEFAULT_PAGE_SIZE, add_wallet: bool = False
) -> List[dict]:
    cursor.skip(skip).limit(limit)
    result = [doc for doc in cursor]
    result = await process_documents(result, add_wallet)
    return result
