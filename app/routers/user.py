from fastapi.security import HTTPBasicCredentials
from app.models import UserData, UserDataDTO
from fastapi import HTTPException, status, APIRouter, Depends
from app.db import user
from sqlalchemy.orm import Session
from .deps import authorize_user, get_db, http_basic_security

user_router = APIRouter(prefix="/user")


@user_router.get("")
async def get_user_info(
    login: str, db: Session = Depends(get_db)
) -> UserDataDTO:
    user_data = user.get_user_data(db, login)
    if user_data is None:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail=f"User {login} not found",
        )
    return UserDataDTO(**user_data.dict())


@user_router.post("")
async def add_user(user_data: UserData, db: Session = Depends(get_db)) -> str:
    if user.add_user(db, user_data) is False:
        raise HTTPException(
            status_code=status.HTTP_406_NOT_ACCEPTABLE,
            detail="Given user already exists!",
        )
    return "OK"


@user_router.delete("")
async def delete_user(
    db: Session = Depends(get_db),
    credentials: HTTPBasicCredentials = Depends(http_basic_security),
) -> str:
    if authorize_user(credentials) is False:
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail=f"Cannot authorize user {credentials.username}",
        )

    if user.delete_user(db, credentials.username) is False:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail=f"Cannot delete user {credentials.username} because it does not exist",
        )

    return "OK"
