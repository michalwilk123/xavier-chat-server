import secrets
from typing import Literal

from fastapi import APIRouter, Depends, status
from fastapi.exceptions import HTTPException

from app.db import contacts, crypto, invites, user
from app.models.invites import InviteModel, InviteResponse
from app.models.user import UserDataDTO
from app.routers.deps import authenticate_user

invites_router = APIRouter(prefix="/invites")


@invites_router.post("")
async def send_invite(
    invite: InviteModel, data=Depends(authenticate_user)
) -> InviteResponse:
    login, db = data
    if secrets.compare_digest(invite.recv_login, login):
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail=(
                f"You are logged as {login} and trying to send "
                "invite to yourself"
            ),
        )

    # Retrieving data about both parties
    sender = user.get_user_data(db, invite.sender_login, get_id=True)
    if sender is None:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail=(
                f"The sender (login: {invite.sender_login}) " "does not exist!"
            ),
        )

    reciever = user.get_user_data(db, invite.recv_login, get_id=True)
    if reciever is None:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail=(
                f"The reciever (login: {invite.recv_login}) " "does not exist!"
            ),
        )

    sender_id, reciever_id = sender.user_id, reciever.user_id

    if sender_id is None or reciever_id is None:
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=(
                f"The users {sender.login} or {reciever.login}"
                " does not possess primary id key in the database"
            ),
        )

    if invites.invite_exists(db, sender_id, reciever_id):
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN,
            detail=(
                f"The user {sender.login} already sent user {reciever.login}"
                " an invite! Wait till the reciever accepts your last request."
            ),
        )

    if invite.otk_index is None:
        res = crypto.get_free_otk(db, invite.recv_login)
        if res is None:
            raise HTTPException(
                status_code=status.HTTP_404_NOT_FOUND,
                detail=(
                    f"User: {invite.recv_login} has no "
                    "one time keys left at his/her hand. "
                    "Try to send your invitations next "
                    "time or contact this user directly "
                ),
            )
        invite.otk_index, otk_val = res
    else:
        otk_val = crypto.get_otk_from_idx(
            db, invite.recv_login, invite.otk_index
        )

    try:
        invites.add_invite(db, invite, sender_id, reciever_id)
    except invites.InviteModelException:
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=("Could not assign the index of one time key"),
        )

    return InviteResponse(
        reciever=UserDataDTO(**sender.dict()),
        otk_index=invite.otk_index,
        otk_key=otk_val,
    )


@invites_router.get("")
async def get_my_invites(data=Depends(authenticate_user)) -> list[InviteModel]:
    login, db = data
    return invites.get_invites(db, login)


@invites_router.post("/answer/{ephem_key}/{decision}")
def respond_to_invite(
    ephem_key: str,
    decision: Literal["accept", "reject"],
    data=Depends(authenticate_user),
):
    login, db = data
    invite_tup = invites.get_invite_by_ephemeral_key(db, login, ephem_key)

    if invite_tup is None:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="could not find an invite with given key/username",
        )

    invite, sender_id, reciever_id = invite_tup

    if decision == "accept":
        if contacts.contact_exists(db, sender_id, reciever_id):
            raise HTTPException(
                status_code=status.HTTP_403_FORBIDDEN,
                detail=(
                    "Users already established a conversation! Creating "
                    "subsequent conversation is forbidden."
                ),
            )
        contacts.create_new_contact(db, sender_id, reciever_id)

    invites.delete_invite(db, sender_id, reciever_id)
    return "OK"
