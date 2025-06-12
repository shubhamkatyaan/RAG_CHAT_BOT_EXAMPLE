# app/db/mongo.py
from motor.motor_asyncio import AsyncIOMotorClient
from app.config import settings

# create a single Mongo client for the whole app
client = AsyncIOMotorClient(settings.mongodb_url)
db = client["complaints_db"]
complaints_coll = db["complaints"]
