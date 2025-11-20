from functools import lru_cache

from dotenv import load_dotenv
from environs import Env

load_dotenv()
env = Env()


class Settings:
    PG_HOST = env.str("PG_HOST")
    PG_PORT = env.int("PG_PORT", 5432)
    PG_USER = env.str("PG_USER")
    PG_PASSWORD = env.str("PG_PASSWORD")
    PG_DB = env.str("PG_DB")

    @property
    def migrate_url(self) -> str:
        return f"postgresql+psycopg://{self.PG_USER}:{self.PG_PASSWORD}@{self.PG_HOST}:{self.PG_PORT}/{self.PG_DB}"

    @property
    def url(self):
        return f"postgresql+psycopg://{self.PG_USER}:{self.PG_PASSWORD}@{self.PG_HOST}:{self.PG_PORT}/{self.PG_DB}"


@lru_cache
def get_settings():
    return Settings()


settings = get_settings()
