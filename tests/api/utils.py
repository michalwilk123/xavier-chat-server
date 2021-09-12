import time
from typing import Optional

from app.models.crypto import FakeJWT, hash_signature


def generate_signature(
    login: str,
    sighash: str,
    expiration_time: int = 1000,
    checksum: Optional[str] = None,
) -> dict:
    signature = FakeJWT(
        expiration_time=expiration_time,
        creation=int(time.time()) - 10,
    )

    if checksum is None:
        signature.checksum = hash_signature(signature, sighash)
    else:
        signature.checksum = checksum

    return {"signature": signature.dict(), "login": login}
