from app.models.contact_model import InviteModel
from typing import List
from .collections import contacts_collection


async def get_past_invites(login: str, signature: str) -> List[InviteModel]:
    ras_list = []

    async for invite in contacts_collection.find(
        {"contact_login": login, "signature": signature}
    ):
        invite["signature"] = None
        ras_list.append(InviteModel(**invite))

    await contacts_collection.delete_many(
        {"login": login, signature: "signature"}
    )
    return ras_list


async def send_invite(invite: InviteModel):
    # deleteting past invites
    await contacts_collection.delete_many(
        {"my_login": invite.my_login, "contact_login": invite.contact_login}
    )
    await contacts_collection.insert_one(invite)
