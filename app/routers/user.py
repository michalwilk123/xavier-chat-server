from fastapi import Body
from app.models.user_model import UserData, UserInfoPayload
from fastapi import APIRouter, HTTPException
from app.db import user
from .crypto import crypto_router

user_router = APIRouter(prefix="/user")


@user_router.get("")
async def user_info(login: str) -> UserInfoPayload:
    user_data = await user.get_user_data(login)
    return UserInfoPayload(user_data=user_data, success=user_data is not None)


@user_router.post("")
async def add_user(user_data: UserData) -> dict:
    if user_data.signature is None:
        raise HTTPException(
            status_code=401,
            detail="You have not provided nessesary signature value to perfom this operation!!",
        )
    await user.add_user(user_data)
    return {"new_user": user_data.login}


@user_router.delete("")
async def delete_user(login: str = Body(...), signature: str = Body(...)) -> dict:
    if not await user.delete_user(login, signature):
        raise HTTPException(
            status_code=401,
            detail=f"Cannot delete user {login} because it does not exist",
        )
    return {"removed": login}


@user_router.get("/exist")
async def user_exist(login: str):
    user_data = await user.get_user_data(login)
    return {"exist": user_data is not None}


user_router.include_router(crypto_router)
