from fastapi.exceptions import HTTPException
from app.models.contact_model import InviteModel, PastInvites
from app.db import contacts
from fastapi import APIRouter
from .user import user_exist
import asyncio

contact_router = APIRouter(prefix="/contacts")


@contact_router.post("")
async def send_invite(invite: InviteModel):
    # if user_exist(invite.my_login) and
    if not all(
        await asyncio.gather(
            user_exist(invite.my_login), user_exist(invite.contact_login)
        )
    ):
        return {"success" : False, "message" : "one of the given users is not registered"}

    await contacts.send_invite(invite)
    return {"success" : True}


@contact_router.get("")
async def get_invites(login: str, signature: str) -> PastInvites:
    inv_list = await contacts.get_past_invites(login, signature)
    return PastInvites(number_of_invites=len(inv_list), invites=inv_list)
