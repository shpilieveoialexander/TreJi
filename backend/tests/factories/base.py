from factory.alchemy import SQLAlchemyModelFactory

from tests.conftests import TestSession


class BaseFactory(SQLAlchemyModelFactory):
    class Meta:
        abstract = True
        sqlalchemy_session = TestSession
        sqlalchemy_session_persistence = "commit"
