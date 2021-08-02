from app.models.user import UserDataDTO
from fastapi.exceptions import HTTPException
from app.models.invites import InviteModel, InviteResponse
from fastapi import APIRouter, Depends, status
from app.routers.deps import authenticate_user
from app.db import user, invites, crypto
import secrets

invites_router = APIRouter(prefix="/invites")


@invites_router.post("")
def send_invite(
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
def get_my_invites(data=Depends(authenticate_user)):
    login, db = data
    return invites.get_invites(db, login)
