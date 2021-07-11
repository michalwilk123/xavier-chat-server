from app.models.user_model import UserData
from typing import List, Optional
from sqlalchemy.orm import Session


class CryptoControllerException(Exception):
    ...


async def _get_otk_keys(db: Session, login: str) -> List[Optional[str]]:
    user_data = await db.users.find_one({"login": login})

    if user_data is None:
        raise KeyError(f"Database does not contain user with login {login}")

    keys = user_data["one_time_keys"]

    if keys is None:
        raise CryptoControllerException(
            "Keys not initialized. Something went terribly wrong"
        )

    if not any(keys):
        raise CryptoControllerException(
            "No key left. Wait for the owner to replenish keys"
        )

    return keys


async def get_otk_key(db: Session, login: str, otk_index: int) -> str:
    otk_list = await _get_otk_keys(db, login)

    if len(otk_list) <= otk_index:
        raise IndexError("Given index is out of bounds")

    result = otk_list[otk_index]
    if result is None:
        raise IndexError("There is not key available at given index")

    return result


async def set_otk_key(
    db: Session,
    login: str,
    otk_index: int,
    /,
    new_otk: Optional[str] = None,
) -> None:
    otk_list = await _get_otk_keys(db, login)

    if len(otk_list) <= otk_index:
        raise IndexError("Given index is out of bounds")

    result = otk_list[otk_index]
    if result is None:
        raise IndexError("The key is already deleted")

    otk_list[otk_index] = new_otk
    res = await db.users.update_one(
        {"login": login}, {"$set": {"one_time_keys": otk_list}}
    )

    if res is None:
        raise CryptoControllerException("User somehow dissapeared")


async def get_available_indexes(db: Session, login: str) -> List[int]:
    otk_list = await _get_otk_keys(db, login)
    return [idx for idx, el in enumerate(otk_list) if el is not None]


async def set_missing_key(db: Session, login: str, key: str, otk_index: int):
    otk_list = await _get_otk_keys(db, login)

    if len(otk_list) <= otk_index:
        raise IndexError("Given index is out of bounds")

    result = otk_list[otk_index]
    if result is not None:
        raise IndexError("The key is already set")

    otk_list[otk_index] = key
    res = await db.users.update_one(
        {"login": login}, {"$set": {"one_time_keys": otk_list}}
    )

    if res is None:
        raise CryptoControllerException("User somehow dissapeared")


def set_one_time_keys(
    db: Session,
    login: str,
    keys: List[Optional[str]],
) -> bool:

    return True
