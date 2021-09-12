from fastapi import APIRouter, Depends, HTTPException, status
from sqlalchemy.orm import Session

from app.db import user
from app.models import UserData, UserDataDTO

from .deps import authenticate_user, get_db

user_router = APIRouter(prefix="/users")


@user_router.get("")
@user_router.get("/{login}")
async def get_user_info(
    login: str, db: Session = Depends(get_db)
) -> UserDataDTO:
    user_data = user.get_user_data(db, login)
    if user_data is None:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail=f"User with the name {login} not found",
        )
    return UserDataDTO(**user_data.dict())


@user_router.post("")
async def add_user(user_data: UserData, db: Session = Depends(get_db)) -> str:
    if user.add_user(db, user_data) is False:
        raise HTTPException(
            status_code=status.HTTP_406_NOT_ACCEPTABLE,
            detail="Could not add the user with the given parameters",
        )
    return "OK"


@user_router.delete("")
async def delete_user(
    data=Depends(authenticate_user), db: Session = Depends(get_db)
) -> str:
    login, db = data

    if user.delete_user(db, login) is False:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail=f"Cannot delete user {login} because it does not exist",
        )

    return "OK"
