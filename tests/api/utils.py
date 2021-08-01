from typing import Optional
from app.models.crypto import ZkSnarkNaive, hash_signature
import time


def generate_signature(
    login: str,
    sighash: str,
    expiration_time: int = 1000,
    check_sum: Optional[str] = None,
) -> dict:
    signature = ZkSnarkNaive(
        expiration_time=expiration_time,
        creation=int(time.time()) - 10,
    )

    if check_sum is None:
        signature.check_sum = hash_signature(signature, sighash)
    else:
        signature.check_sum = check_sum

    return {"signature": signature.dict(), "login": login}
