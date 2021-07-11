from pydantic import BaseModel
from typing import Optional


class InviteModel(BaseModel):
    my_login: str
    signature: str
    contact_login: str
    public_id_key: str
    public_ephemeral_key: str
    otk_index: int


class InviteModelDBO(BaseModel):
    login: str
    public_id_key: str
    public_ephemeral_key: str
    otk_index: int
