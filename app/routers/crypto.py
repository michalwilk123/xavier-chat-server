from typing import Any
from fastapi import APIRouter, HTTPException
from app.models.otk import OtkModel, OtkInitialModel
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
    ...
    return {}


@crypto_router.put("/one-time-key")
async def set_otk(otk_model: OtkModel):

    return {"response": "success"}


@crypto_router.post("/one-time-key")
async def set_init_otk_keys(initial: OtkInitialModel) -> dict:
    return {}


@crypto_router.get("/one-time-key-list")
async def get_available_indexes(contact: str):
    return {}
