from inspect import signature
from pydantic import BaseModel
from typing import List, Optional


class OtkModel(BaseModel):
    login: str
    signature: str
    one_time_public_key: str
    otk_index: int


class OtkInitialModel(BaseModel):
    login: str
    signature: str
    num_of_keys: int
    one_time_public_keys: List[Optional[str]]


class OtkRequestModel(BaseModel):
    login: str
    signature: str
    otk_index: int
