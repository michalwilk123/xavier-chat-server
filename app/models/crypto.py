from typing import Optional, List
from pydantic import BaseModel
from fastapi import Query
import hashlib
import secrets


class SignatureError(Exception):
    ...


class OtkSimple(BaseModel):
    index: int = Query(..., le=100)
    value: str = Query(..., max_length=100, min_length=8)


class OtkCollection(BaseModel):
    collection: List[OtkSimple]


class ZkSnarkNaive(BaseModel):
    """
    THIS IS INCORRECT ZK SNARK!
    IT IS NOT SAFE AT ALL.

    We are assigning the expiration date
    (POSIX time) for signature. To verify that message was not
    tampered, we adding a check sum to verify the authenticity
    of original message.

    Check sum is calculated with initial secret, like in jwt.

    NOTE: should implement also some kind of pepper
    """

    expiration_time: int
    creation: int
    check_sum: Optional[str]


def hash_signature(sign: ZkSnarkNaive, secret: str) -> str:
    # NOTE : should switch in future to bcrypt or argon2
    return hashlib.sha256(
        (
            f"Expiration: {sign.expiration_time} | "
            f"Created: {int(sign.creation)} | "
            f"Secret: {secret}"
        ).encode("utf-8")
    ).hexdigest()


def validate_signature(sign: ZkSnarkNaive, secret: str) -> bool:
    if sign.check_sum is None:
        raise SignatureError(
            "The checksum must be provided for the"
            " signature if you wish to validate it"
        )
    return secrets.compare_digest(sign.check_sum, hash_signature(sign, secret))
