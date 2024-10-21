import os
from pymongo import MongoClient
from dotenv import load_dotenv

load_dotenv()

MONGO_INITDB_DATABASE = os.getenv('MONGO_INITDB_DATABASE')
MONGO_INITDB_ROOT_USERNAME = os.getenv('MONGO_INITDB_ROOT_USERNAME')
MONGO_INITDB_ROOT_PASSWORD = os.getenv('MONGO_INITDB_ROOT_PASSWORD')
MONGO_HOST = os.getenv('MONGO_HOST')

if not all([MONGO_INITDB_DATABASE, MONGO_INITDB_ROOT_USERNAME, MONGO_INITDB_ROOT_PASSWORD, MONGO_HOST]):
    raise ValueError("One or more required environment variables are missing.")

try:
    client = MongoClient(
        host=MONGO_HOST,
        port=27017,
        username=MONGO_INITDB_ROOT_USERNAME,
        password=MONGO_INITDB_ROOT_PASSWORD
    )
    db = client[MONGO_INITDB_DATABASE]
    user_collection = db['users_affiliate3']
    wallet_collection = db['users_wallet']
    payout_collection = db['payout_affiliate']
    print("Database connection established successfully.")
except Exception as e:
    print(f"Failed to connect to the database: {str(e)}")
    raise
