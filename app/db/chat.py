from typing import List
from sqlalchemy.orm import Session


async def send_chat_message_to_absent_user(
    db: Session, login: str, message: str
):
    ...


async def get_pending_messages(db: Session, login: str) -> List[dict]:
    return []
