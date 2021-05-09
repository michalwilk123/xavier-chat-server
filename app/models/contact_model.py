from pydantic import BaseModel
from typing import List, Optional


class InviteModel(BaseModel):
    """
    New contact invite model
    """

    my_login: str
    signature: Optional[str]
    contact_login: str
    public_id_key: str
    public_ephemeral_key: str
    otk_index: int


class PastInvites(BaseModel):
    number_of_invites: int
    invites: List[InviteModel]
