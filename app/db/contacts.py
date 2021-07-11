from fastapi.exceptions import HTTPException
from starlette import status
from app.models.contact_model import InviteModel
from typing import List
from .user import get_user_data
import secrets
from sqlalchemy.orm import Session


async def get_invites(
    db: Session, login: str, signature: str
) -> List[InviteModel]:
    ras_list = []

    async for invite in db.contacts.find(
        {"contact_login": login, "signature": signature}
    ):
        invite["signature"] = None
        ras_list.append(InviteModel(**invite))

    await db.contacts.delete_many({"login": login, signature: "signature"})
    return ras_list


async def store_invite(db: Session, invite: InviteModel) -> bool:
    my_info = await get_user_data(db, invite.my_login)

    if my_info is None:
        return False

    if secrets.compare_digest(my_info.signature, invite.signature) is False:
        return False

    # deleteting past invites
    await db.contacts.delete_many(
        {"my_login": invite.my_login, "contact_login": invite.contact_login}
    )
    await db.contacts.insert_one(invite.dict())
    return True
