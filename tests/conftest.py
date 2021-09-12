from app.main import app
from app.routers.deps import get_db
from fastapi.testclient import TestClient
from sqlalchemy.orm import Session, sessionmaker
from sqlalchemy import create_engine, event
from app.db.database import Base
from sqlalchemy.engine import Engine


# Because of lack of support of foreign keys in sqlite we MUST EXPLICILY
# perform pragma on this dbms :^)
@event.listens_for(Engine, "connect")
def set_sqlite_pragma(dbapi_connection, connection_record):
    cursor = dbapi_connection.cursor()
    cursor.execute("PRAGMA foreign_keys=ON")
    cursor.close()


SQLALCHEMY_DATABASE_URL = "sqlite:///./test.db"
TEST_SECRET = "d3n983n28br387dn83n3n28"

engine = create_engine(
    SQLALCHEMY_DATABASE_URL,
    connect_args={"check_same_thread": False},
    echo=False,
)
TestingSessionLocal = sessionmaker(autocommit=False, autoflush=False, bind=engine)

Base.metadata.create_all(bind=engine)


def override_get_db() -> Session:
    db = TestingSessionLocal()
    try:
        yield db
    finally:
        db.close()


test_client = TestClient(app)

app.dependency_overrides[get_db] = override_get_db
