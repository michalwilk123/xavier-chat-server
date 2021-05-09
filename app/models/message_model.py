from pydantic import BaseModel
from enum import Enum


class MessageType(Enum):
    TEXT_MESSAGE = 1
    X3DH_SESSION_START = 2
    X3DH_SESSION_HANDSHAKE = 3
    AUTH = 4


class MessageHeaderModel(BaseModel):
    message_type: MessageType
    sender: str
    posix_time_send: int


class MessageBodyModel(BaseModel):
    content: str
    public_key: str


class MessageModel(BaseModel):
    head: MessageHeaderModel
    body: MessageBodyModel
