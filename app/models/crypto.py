import hashlib
import secrets
from typing import List, Optional

from fastapi import Query
from pydantic import BaseModel


class SignatureError(Exception):
    ...


class OtkSimple(BaseModel):
    index: int = Query(..., le=100)
    value: str = Query(..., max_length=100, min_length=8)


class OtkCollection(BaseModel):
    collection: List[OtkSimple]


class FakeJWT(BaseModel):
    """
    We are assigning the expiration date
    (POSIX time) for signature. To verify that message was not
    tampered, we adding a check sum to verify the authenticity
    of original message.

    Check sum is calculated with initial secret, like in jwt.

    NOTE: should implement also some kind of pepper
    """

    expiration_time: int
    creation: int
    checksum: Optional[str]


def hash_signature(sign: FakeJWT, secret: str) -> str:
    # NOTE : should switch in future to bcrypt or argon2
    return hashlib.sha256(
        (
            f"Expiration: {sign.expiration_time} | "
            f"Created: {int(sign.creation)} | "
            f"Secret: {secret}"
        ).encode("utf-8")
    ).hexdigest()


def validate_signature(sign: FakeJWT, secret: str) -> bool:
    if sign.checksum is None:
        raise SignatureError(
            "The checksum must be provided for the"
            " signature if you wish to validate it"
        )
    return secrets.compare_digest(sign.checksum, hash_signature(sign, secret))
