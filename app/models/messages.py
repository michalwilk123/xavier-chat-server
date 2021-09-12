import time
from typing import List, Optional

from pydantic import BaseModel


class SingleMessage(BaseModel):
    created: int = int(time.time())
    content: str
    public_key: Optional[str]


class MessagePackage(BaseModel):
    sender: str
    reciever: str
    messages: List[SingleMessage]
    handshake_digest: Optional[str]


class SingleContact(BaseModel):
    contact_name: str
    conversation_channel: str
