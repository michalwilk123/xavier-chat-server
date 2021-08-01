from pydantic import BaseModel
from enum import Enum

MessageType = Enum(
    "MessageType",
    "TEXT_MESSAGE X3DH_SESSION_START X3DH_SESSION_HANDSHAKE AUTH",
)


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
