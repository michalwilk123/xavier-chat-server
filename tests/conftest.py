from app.routers.deps import get_db
from app.config import get_settings
from httpx import AsyncClient
from app.main import app
from fastapi.testclient import TestClient
import pytest
from sqlalchemy.orm import Session, sessionmaker
from sqlalchemy import create_engine
from app.db.database import Base


SQLALCHEMY_DATABASE_URL = "sqlite:///./test.db"

engine = create_engine(
    SQLALCHEMY_DATABASE_URL, connect_args={"check_same_thread": False}
)
TestingSessionLocal = sessionmaker(
    autocommit=False, autoflush=False, bind=engine
)

Base.metadata.create_all(bind=engine)


@pytest.fixture(scope="session")
def async_client():
    return AsyncClient(app=app, base_url=get_settings().base_url)


def override_get_db() -> Session:
    db = TestingSessionLocal()
    try:
        yield db
    finally:
        db.close()


client = TestClient(app)

app.dependency_overrides[get_db] = override_get_db
