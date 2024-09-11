from pydantic import AnyUrl


class PostgresDsn(AnyUrl):
    allowed_schemes = {
        "postgres",
        "postgresql",
        "postgresql+asyncpg",
        "postgresql+psycopg2",
    }
    user_required = True
