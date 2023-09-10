import os
from pydantic_settings import BaseSettings, SettingsConfigDict


class Options(BaseSettings):
    model_config = SettingsConfigDict(
        env_prefix='agnostic_'
    )

    db_dialect: str | None = 'postgresql+asyncpg'
    db_username: str | None = 'postgres'
    db_password: str | None = 'postgres'
    db_host: str | None = 'localhost'
    db_port: int | None = 5432
    db_database: str | None = 'agnostic'

    web_host: str | None = '0.0.0.0'
    web_port: int | None = 8000

    production: bool | None = True


options = Options()
