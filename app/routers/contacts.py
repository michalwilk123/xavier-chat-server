from app.models.contact_model import InviteModel, InviteModelDBO
from fastapi import APIRouter, Depends, HTTPException, status
from app.db.contacts import store_invite, get_invites
from typing import List
from sqlalchemy.orm import Session
from .deps import get_db

contact_router = APIRouter(prefix="/contacts")


@contact_router.post("")
async def send_invite(invite: InviteModel, db: Session = Depends(get_db)):
    # if None in await asyncio.gather(
    #     get_user_data(db, invite.my_login),
    #     get_user_data(db, invite.contact_login),
    # ):
    #     raise HTTPException(
    #         status_code=status.HTTP_404_NOT_FOUND,
    #         detail="Cannot find users with given logins",
    #     )
    # if await store_invite(db, invite) is False:
    #     raise HTTPException(status_code=status.HTTP_401_UNAUTHORIZED)

    return "OK"


@contact_router.get("")
async def get_prev_invites(
    login: str, signature: str, db: Session = Depends(get_db)
) -> List[InviteModelDBO]:
    # invites = await get_invites(db, login, signature)
    # return [InviteModelDBO(**inv.dict()) for inv in invites]
    return []
