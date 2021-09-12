from typing import Optional

from pydantic import BaseModel

from .user import UserDataDTO


class InviteModel(BaseModel):
    sender_login: str
    recv_login: str
    public_id_key: str
    public_ephemeral_key: str
    otk_index: Optional[int]
    additional_msg: str


class InviteResponse(BaseModel):
    reciever: UserDataDTO
    otk_index: int
    otk_key: str
