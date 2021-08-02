from app.models import UserData, UserDataDTO
from fastapi import HTTPException, status, APIRouter, Depends
from app.db import user
from sqlalchemy.orm import Session
from .deps import get_db, authenticate_user

user_router = APIRouter(prefix="/users")


@user_router.get("")
@user_router.get("/{login}")
def get_user_info(login: str, db: Session = Depends(get_db)) -> UserDataDTO:
    user_data = user.get_user_data(db, login)
    if user_data is None:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail=f"User with the name {login} not found",
        )
    return UserDataDTO(**user_data.dict())


@user_router.post("")
def add_user(user_data: UserData, db: Session = Depends(get_db)) -> str:
    if user.add_user(db, user_data) is False:
        raise HTTPException(
            status_code=status.HTTP_406_NOT_ACCEPTABLE,
            detail="Could not add the user with the given parameters",
        )
    return "OK"


@user_router.delete("")
def delete_user(
    data=Depends(authenticate_user), db: Session = Depends(get_db)
) -> str:
    login, db = data

    if user.delete_user(db, login) is False:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail=f"Cannot delete user {login} because it does not exist",
        )

    return "OK"
