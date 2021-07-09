from fastapi import HTTPException, status
from fastapi.param_functions import Depends
from fastapi.security import HTTPBasicCredentials
from app.models.user_model import UserData, UserDataDTO
from fastapi import APIRouter, HTTPException
from app.db import user
from .crypto import crypto_router, security

user_router = APIRouter(prefix="/user")


@user_router.get("")
async def user_info(login: str) -> UserDataDTO:
    user_data = await user.get_user_data(login)
    if user_data is None:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail=f"User {login} not found")
    user_data.signature = None
    user_data.one_time_keys = None
    return UserDataDTO(**user_data.dict())


@user_router.post("")
async def add_user(user_data: UserData) -> str:
    if user_data.signature is None:
        raise HTTPException(
            status_code=401,
            detail="You have not provided nessesary signature value to perfom this operation!!",
        )
    if await user.add_user(user_data) is False:
        raise HTTPException(
            status_code=status.HTTP_406_NOT_ACCEPTABLE,
            detail="Given user already exists!",
        )
    return "OK"


@user_router.delete("")
async def delete_user(
    credentials:HTTPBasicCredentials=Depends(security)
) -> str:
    if not await user.delete_user(credentials.username, credentials.password):
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail=f"Cannot delete user {credentials.username} because it does not exist",
        )
    return "OK"


user_router.include_router(crypto_router)
