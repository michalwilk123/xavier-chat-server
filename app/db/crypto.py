from app.models.user_model import UserData
from typing import List, Optional
from .collections import user_collection


class CryptoControllerException(Exception):
    ...


async def _get_otk_keys(login: str) -> List[Optional[str]]:
    user_data = await user_collection.find_one({"login": login})

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


async def get_otk_key(login: str, otk_index: int) -> str:
    otk_list = await _get_otk_keys(login)

    if len(otk_list) >= otk_index:
        raise IndexError("Given index is out of bounds")

    result = otk_list[otk_index]
    if result is None:
        raise IndexError("There is not key available at given index")

    return result


async def set_otk_key(
    login: str, otk_index: int, /, new_otk: Optional[str] = None
) -> None:
    otk_list = await _get_otk_keys(login)

    if len(otk_list) >= otk_index:
        raise IndexError("Given index is out of bounds")

    result = otk_list[otk_index]
    if result is None:
        raise IndexError("The key is already deleted")

    otk_list[otk_index] = new_otk
    res = await user_collection.update_one(
        {"login": login}, {"$set": {"one_time_keys": otk_list}}
    )

    if res is None:
        raise CryptoControllerException("User somehow dissapeared")


async def get_available_indexes(login: str) -> List[int]:
    otk_list = await _get_otk_keys(login)
    return [idx for idx, el in enumerate(otk_list) if el is not None]


async def set_missing_key(login: str, key: str, otk_index: int):
    otk_list = await _get_otk_keys(login)

    if len(otk_list) >= otk_index:
        raise IndexError("Given index is out of bounds")

    result = otk_list[otk_index]
    if result is not None:
        raise IndexError("The key is already set")

    otk_list[otk_index] = key
    res = await user_collection.update_one(
        {"login": login}, {"$set": {"one_time_keys": otk_list}}
    )

    if res is None:
        raise CryptoControllerException("User somehow dissapeared")


async def set_init_otk_keys(
    login: str, signature: str, keys: List[Optional[str]]
) -> bool:
    res = await user_collection.update_one(
        {"login": login, "signature": signature},
        {"$set": {"one_time_keys": keys, "number_of_otk": len(keys)}},
    )

    return res is not None
