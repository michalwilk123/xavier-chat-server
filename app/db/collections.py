from motor import motor_asyncio
from app.config import MONGO_URL

mongo_client = motor_asyncio.AsyncIOMotorClient(MONGO_URL)

db = mongo_client.chat

message_collection = db.messages
user_collection = db.users
contacts_collection = db.contacts
