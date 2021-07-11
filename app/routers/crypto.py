from app.db.user import user_auth
from typing import Any
from fastapi import APIRouter, HTTPException
from app.models.otk_model import OtkModel, OtkInitialModel
from app.db import crypto

crypto_router = APIRouter(prefix="/crypto")


def exception_dispatcher(e: Exception) -> Any:
    if type(e) == crypto.CryptoControllerException:
        return HTTPException(status_code=503, detail=f"Problem with keys: {e}")
    elif type(e) == IndexError:
        return HTTPException(
            status_code=403, detail=f"Problem with index: {e}"
        )
    elif type(e) == KeyError:
        return HTTPException(status_code=403, detail=f"User error: {e}")


@crypto_router.get("/one-time-key")
async def get_otk(login: str, index: int) -> dict:
    try:
        otk_key = await crypto.get_otk_key(login, index)
    except (IndexError, KeyError, crypto.CryptoControllerException) as e:
        raise exception_dispatcher(e)

    await crypto.set_otk_key(login, index)
    return {"one_time_key": otk_key}


@crypto_router.put("/one-time-key")
async def set_otk(otk_model: OtkModel):
    if not await user_auth(otk_model.login, otk_model.signature):
        return {"response": "not-authorized"}

    try:
        await crypto.set_otk_key(
            otk_model.login,
            otk_model.otk_index,
            new_otk=otk_model.one_time_public_key,
        )
    except (IndexError, KeyError, crypto.CryptoControllerException) as e:
        raise exception_dispatcher(e)

    return {"response": "success"}


@crypto_router.post("/one-time-key")
async def set_init_otk_keys(initial: OtkInitialModel) -> dict:
    res = await crypto.set_init_otk_keys(
        login=initial.login,
        signature=initial.signature,
        keys=initial.one_time_public_keys,
    )
    return {"success": res}


@crypto_router.get("/one-time-key-list")
async def get_available_indexes(contact: str):
    return {"available_indexes": await crypto.get_available_indexes(contact)}
