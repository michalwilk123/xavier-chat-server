from fastapi.security import HTTPBasicCredentials
from app.db.database import SessionLocal
from typing import Generator
from fastapi.security import HTTPBasic


http_basic_security = HTTPBasic()


def get_db() -> Generator:
    db = SessionLocal()
    try:
        yield db
    finally:
        db.close()


# def authorize_user(credentials: HTTPBasicCredentials) -> HTTPBasicCredentials:
def authorize_user(credentials: HTTPBasicCredentials) -> bool:
    return True
