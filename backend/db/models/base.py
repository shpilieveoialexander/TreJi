from sqlalchemy import Column, DateTime, Integer
from sqlalchemy.ext.declarative import declarative_base

from db.utils import get_default_now

Base = declarative_base()


class BaseModel(Base):
    """Base model"""

    __abstract__ = True

    id = Column(Integer, primary_key=True, index=True, doc="Unique element's ID or PK")
    created_at = Column(
        DateTime,
        nullable=False,
        default=get_default_now,
        doc="Created at",
    )
