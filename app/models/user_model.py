from typing import List, Optional
from pydantic import BaseModel


class UserData(BaseModel):
    login: str
    public_id_key: str
    public_signed_pre_key: str
    signature: Optional[str]
    number_of_otk: int
    one_time_keys: Optional[List[str]]


class BasicUserAuthorization(BaseModel):
    login: str
    signature: str


class UserDataDTO(BaseModel):
    login: str
    public_id_key: str
    public_signed_pre_key: str
    number_of_otk: int
