from typing import List, Optional

from pydantic import BaseModel


class OrmUserData(BaseModel):
    login: str
    public_id_key: str
    public_signed_pre_key: str
    signature: str

    class Config:
        orm_mode = True


class UserData(OrmUserData):
    user_id: Optional[int]
    one_time_keys: List[str]


class UserDataDTO(BaseModel):
    login: str
    public_id_key: str
    public_signed_pre_key: str
