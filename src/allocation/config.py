from functools import lru_cache

from pydantic import BaseSettings


class Config(BaseSettings):
    postgres_uri: str
    api_url: str

    class Config:
        env_file = 'config/.env'


@lru_cache
def get_config() -> Config:
    return Config()
