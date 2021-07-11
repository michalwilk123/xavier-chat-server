from functools import lru_cache
from pydantic import BaseSettings


@lru_cache
def get_settings():
    return Settings()


class Settings(BaseSettings):
    sqlalchemy_database_url: str
    base_url: str

    class Config:
        env_file = ".env"


class AppInformation(BaseSettings):
    APP_NAME: str = "Xavier"
    VERSION: str = "0.1"
    DESCRIPTION = "Backend of the end2end communicator"
