from app.models.user import UserData
from fastapi.params import Body, Depends
from app.models.crypto import ZkSnarkNaive, validate_signature
from sqlalchemy.orm import Session
from fastapi import HTTPException, status, Body
from app.db.user import get_user_data
from app.db.database import SessionLocal
import time
from typing import Generator, Optional, Tuple, Generator


def get_db() -> Generator:
    db = SessionLocal()
    try:
        yield db
    finally:
        db.close()


def authenticate_user(
    signature: ZkSnarkNaive,
    login: str = Body(...),
    db: Session = Depends(get_db),
) -> Tuple[str, Session]:
    exception = HTTPException(status_code=status.HTTP_401_UNAUTHORIZED)

    if signature.check_sum is None:
        exception.detail = "User did not provide a check sum of the signature"
        raise exception

    if time.time() > signature.expiration_time + signature.creation:
        exception.detail = ("The signature has expired.",)
        raise exception

    user_data: Optional[UserData] = get_user_data(db, login)
    if user_data is None:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Given user does not exist",
        )

    if validate_signature(signature, user_data.signature) is False:
        exception.detail = ("Check sum failed. Cannot authorize the user",)
        raise exception

    return login, db
