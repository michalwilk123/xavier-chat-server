from typing import List
from .collections import message_collection


async def send_chat_message_to_absent_user(login: str, message: str):
    await message_collection.insert_one(message)


async def get_pending_messages(login: str) -> List[dict]:
    res = message_collection.find({"login": login})
    messages = await res.to_list(length=1000)
    return messages
