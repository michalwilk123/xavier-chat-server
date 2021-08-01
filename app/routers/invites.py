from app.models.user import UserDataDTO
from fastapi.exceptions import HTTPException
from app.models.invites import InviteModel, InviteResponse
from fastapi import APIRouter, Depends, status
from app.routers.deps import authenticate_user
from app.db.invites import add_invite
from app.db import user
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
            detail=(f"You are logged as {login} and trying to send "
                "invite to yourself"),
        )

    invite_data = add_invite(db, invite)

    if not invite_data:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail=(
                "Invite data was not structured properly. "
                "Or some users (fields: sender_login, "
                "recv_login) or one time keys (otk_index) "
                "were not present in the database"
            ),
        )

    user_data = user.get_user_data(db, login)
    if user_data is None:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail=("The date about the user is lost."),
        )

    return InviteResponse(
        reciever=UserDataDTO(**user_data.dict()), **invite_data
    )


@invites_router.get("")
def get_invites(data=Depends(authenticate_user)):
    login, db = data
    return "OK"
    # return get_invites(db, login)
