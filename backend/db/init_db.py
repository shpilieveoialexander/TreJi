import logging

from sqlalchemy_utils import create_database, database_exists
from tenacity import (after_log, before_log, retry, stop_after_attempt,
                      wait_fixed)

from service.core import settings

logging.basicConfig(format="%(levelname)s:    %(message)s", level=logging.INFO)
logger = logging.getLogger(__name__)

max_tries = 60 * 5  # 5 minutes
wait_seconds = 1


@retry(
    stop=stop_after_attempt(max_tries),
    wait=wait_fixed(wait_seconds),
    before=before_log(logger, logging.INFO),
    after=after_log(logger, logging.WARN),
)
def create_db() -> None:
    """Create DB if not exists"""
    # Checking existing DB
    logger.info("Checking existing database")
    if database_exists(settings.PSQL_DB_URI):
        logger.warning(f"{settings.PSQL_DB_URI} exist")
        return
    # Create DB
    logger.info("Creating new database")
    create_database(settings.PSQL_DB_URI)
    logger.info(f"{settings.PSQL_DB_URI} was created")


if __name__ == "__main__":
    create_db()
