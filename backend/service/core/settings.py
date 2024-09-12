import os
from typing import Any, Final, List, Optional

import ujson
from pydantic import AnyHttpUrl, ConfigDict, field_validator
from pydantic_settings import BaseSettings


class Settings(BaseSettings):
    ###########
    # BACKEND #
    ###########
    SERVER_HOST: str = os.getenv("SERVER_HOST")
    BACKEND_HOST: str = os.getenv("BACKEND_HOST", "0.0.0.0")
    BACKEND_PORT: int = os.getenv("BACKEND_PORT", 8000)

    PROJECT_NAME: str = os.getenv("PROJECT_NAME")
    VERSION: str = os.getenv("VERSION")

    SECRET_KEY: str = os.getenv("SECRET_KEY", "very_secret_key")

    DEBUG: bool = os.getenv("DEBUG", True)

    DEFAULT_TIME_ZONE: str = os.getenv("DEFAULT_TIME_ZONE", "UTC")

    # BACKEND_CORS_ORIGINS is a JSON-formatted list of origins
    # e.g: '["http://localhost", "http://localhost:4200", "http://localhost:3000"]'
    BACKEND_CORS_ORIGINS: List[AnyHttpUrl] = []

    @field_validator("BACKEND_CORS_ORIGINS")
    def parse_cors_origins(cls, value: str) -> List[str]:
        if isinstance(value, str):
            return ujson.loads(value)
        elif isinstance(value, (list, str)):
            return value

    #######
    # JWT #
    #######
    HASH_ALGORITHM: str = "HS256"
    JWT_ACCESS_TOKEN_EXPIRE_MINUTES: int = 60 * 24  # 1 day
    JWT_REFRESH_TOKEN_EXPIRE_MINUTES: int = 60 * 24 * 30  # 1 month

    #############
    # TMP TOKEN #
    #############
    TMP_TOKEN_LIFETIME: int = 30  # 30 minutes

    #############
    # DATABASES #
    #############
    # PSQL
    PSQL_SERVER: str
    PSQL_USER: str
    PSQL_PASSWORD: str
    PSQL_DB_NAME: str
    PSQL_TEST_DB_NAME: str = "test_db"
    PSQL_DB_URI: Optional[str] = None
    PSQL_TEST_DB_URI: Optional[str] = None

    @field_validator("PSQL_DB_URI")
    def build_db_uri(cls, v: Optional[str], info: ConfigDict) -> Any:
        values = info.data
        if isinstance(v, str):
            return v
        return "postgresql+psycopg2://{}:{}@{}:5432/{}".format(
            values.get("PSQL_USER"),
            values.get("PSQL_PASSWORD"),
            values.get("PSQL_SERVER"),
            values.get("PSQL_DB_NAME"),
        )

    @field_validator("PSQL_TEST_DB_URI")
    def build_test_db_uri(cls, v: Optional[str], info: ConfigDict) -> Any:
        values = info.data
        if isinstance(v, str):
            return v
        return "postgresql+psycopg2://{}:{}@{}:5432/{}".format(
            values.get("PSQL_USER"),
            values.get("PSQL_PASSWORD"),
            values.get("PSQL_SERVER"),
            values.get("PSQL_TEST_DB_NAME"),
        )

    # Redis
    REDIS_HOST: str = os.getenv("REDIS_HOST")
    REDIS_PORT: int = os.getenv("REDIS_PORT", 6379)
    REDIS_DB: int = os.getenv("REDIS_DB")

    REDIS_CACHE_URL: Final[str] = f"redis://redis"
    REDIS_CACHE_LIFETIME: int = 10  # Set in minutes

    ###########
    # ADMINER #
    ###########
    ADMINER_PORT: int = os.getenv("ADMINER_PORT")

    #########
    # EMAIL #
    #########
    SMTP_PORT: int = os.getenv("SMTP_PORT")
    SMTP_HOST: str = os.getenv("SMTP_HOST")
    SMTP_USER: str = os.getenv("SMTP_USER")
    SMTP_PASSWORD: str = os.getenv("SMTP_PASSWORD")

    class Config:
        case_sensitive = True


settings = Settings()
