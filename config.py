from functools import lru_cache

from pydantic import BaseSettings


class Config(BaseSettings):
    postgres_uri: str
    api_url: str = 'http://127.0.0.1:5005'

    class Config:
        env_file = 'config/.env'


@lru_cache
def get_config() -> Config:
    return Config()
