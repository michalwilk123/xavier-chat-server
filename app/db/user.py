from typing import Optional
from app.models.user_model import UserData
from .collections import user_collection


class UserDataException(Exception):
    ...


async def add_user(user: UserData) -> bool:
    res = await user_collection.find_one({"login": user.login})
    if res is not None:
        return False
    await user_collection.insert_one(dict(user))
    return True


async def delete_user(user: str, signature: str) -> bool:
    result = await user_collection.find_one_and_delete(
        {"login": user, "signature": signature}
    )
    return result is not None


async def get_user_data(user: str) -> Optional[UserData]:
    result = await user_collection.find_one({"login": user})

    if result is None:
        return None
    return UserData(**result)


async def user_auth(login: str, signature: str) -> bool:
    res = await user_collection.find_one(
        {"login": login, "signature": signature}
    )
    return res is not None
