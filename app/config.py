from functools import lru_cache

from pydantic import BaseSettings


@lru_cache
def get_settings():
    return Settings()


class Settings(BaseSettings):
    base_url: str
    redis_password: str
    postgres_db: str
    broadcaster_source: str

    class Config:
        env_file = ".env"


class AppInformation(BaseSettings):
    APP_NAME: str = "Xavier"
    VERSION: str = "0.1"
    DESCRIPTION = "Backend of the end2end communicator"
