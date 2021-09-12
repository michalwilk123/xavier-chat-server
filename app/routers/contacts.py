from fastapi import APIRouter, Depends

from app.db import contacts
from app.models.messages import SingleContact
from app.routers.deps import authenticate_user

contacts_router = APIRouter(prefix="/contacts")


@contacts_router.get("")
async def get_user_contacts(
    data=Depends(authenticate_user),
) -> list[SingleContact]:
    login, db = data
    return contacts.get_contacts(db, login)
