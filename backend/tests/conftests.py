import unittest

from fastapi.testclient import TestClient
from sqlalchemy import create_engine
from sqlalchemy.orm import scoped_session, sessionmaker
from sqlalchemy_utils import create_database, database_exists, drop_database

from db.models import BaseModel
from service.core import settings
from service.core.dependencies import get_session
from service.main import app

# Create test engine
test_engine = create_engine(settings.PSQL_TEST_DB_URI, pool_pre_ping=True)
# Create test Session
TestSession = scoped_session(
    sessionmaker(autocommit=False, autoflush=False, bind=test_engine)
)


def get_test_db():
    # Function for overwrite get_db() dependencies which return a normal Session
    return TestSession


class BaseTestCase(unittest.TestCase):
    client = None

    @classmethod
    def setUpClass(cls) -> None:
        cls.addClassCleanup(drop_database, settings.PSQL_TEST_DB_URI)
        if not database_exists(settings.PSQL_TEST_DB_URI):
            # Crete test database
            create_database(settings.PSQL_TEST_DB_URI)
        # with test_engine.connect() as connection:
        #     connection.execute(text("CREATE EXTENSION IF NOT EXISTS postgis;"))
        #     connection.commit()

    @classmethod
    def tearDownClass(cls) -> None:
        for table in reversed(BaseModel.metadata.sorted_tables):
            TestSession.execute(table.delete())
        TestSession.commit()


class TestCase(BaseTestCase):
    @classmethod
    def setUpClass(cls) -> None:
        super().setUpClass()
        # Overwrite get_db() dependencies
        app.dependency_overrides[get_session] = get_test_db
        # Create client with overwrited get_db()
        cls.client = TestClient(app)
        # Add test session to body
        cls.session = get_test_db
        # Create all tables
        BaseModel.metadata.create_all(test_engine)

    @classmethod
    def tearDown(self) -> None:
        with test_engine.connect() as connection:
            for table in reversed(BaseModel.metadata.sorted_tables):
                connection.execute(table.delete())
            connection.commit()
