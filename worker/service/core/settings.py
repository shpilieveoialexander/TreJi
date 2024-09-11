import os
from typing import Any, Dict, Final, Optional

from pydantic import validator
from pydantic_settings import BaseSettings


class Settings(BaseSettings):
    #################
    # CELERY WORKER #
    #################
    SERVER_HOST: str = os.getenv("SERVER_HOST")
    BACKEND_HOST: str = os.getenv("BACKEND_HOST", "0.0.0.0")

    PROJECT_NAME: str = os.getenv("PROJECT_NAME")

    DEBUG: bool = os.getenv("DEBUG", True)

    DEFAULT_TIME_ZONE: str = os.getenv("DEFAULT_TIME_ZONE", "UTC")

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

    @validator("PSQL_DB_URI", pre=True)
    def build_db_uri(cls, v: Optional[str], values: Dict[str, Any]) -> Any:
        if isinstance(v, str):
            return v
        return f"postgresql+psycopg2://{values.get('PSQL_USER')}:{values.get('PSQL_PASSWORD')}@{values.get('PSQL_SERVER')}:5432/{values.get('PSQL_DB_NAME')}"

    @validator("PSQL_TEST_DB_URI", pre=True)
    def build_test_db_uri(cls, v: Optional[str], values: Dict[str, Any]) -> Any:
        if isinstance(v, str):
            return v
        return f"postgresql+psycopg2://{values.get('PSQL_USER')}:{values.get('PSQL_PASSWORD')}@{values.get('PSQL_SERVER')}:5432/{values.get('PSQL_TEST_DB_NAME')}"

    # Redis
    REDIS_HOST: str = os.getenv("REDIS_HOST")
    REDIS_PORT: int = os.getenv("REDIS_PORT", 6379)
    REDIS_DB: int = os.getenv("REDIS_DB")

    REDIS_CACHE_URL: Final[str] = f"redis://redis"
    REDIS_CACHE_LIFETIME: int = 10  # Set in minutes

    class Config:
        case_sensitive = True


settings = Settings()
