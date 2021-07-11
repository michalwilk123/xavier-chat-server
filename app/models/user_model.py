from typing import List, Optional
from pydantic import BaseModel


class UserData(BaseModel):
    login: str
    public_id_key: str
    public_signed_pre_key: str
    signature: str
    one_time_keys: List[Optional[str]]

    class Config:
        orm_mode = True


class UserDataDTO(BaseModel):
    login: str
    public_id_key: str
    public_signed_pre_key: str
