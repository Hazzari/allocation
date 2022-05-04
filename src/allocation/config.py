from functools import lru_cache

from pydantic import BaseSettings


class Config(BaseSettings):
    postgres_uri: str = 'postgresql+psycopg2://allocation:abc1234@127.0.0.1:5432/allocation'
    api_url: str = 'http://127.0.0.1:5005'

    class Config:
        env_file = '../../config/.env'
        # orm_mode = True


@lru_cache
def get_config() -> Config:
    return Config()
