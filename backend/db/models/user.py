from sqlalchemy import Column, Enum, String

from db import constants

from .base import BaseModel


class User(BaseModel):
    """User table"""

    __tablename__ = "user"

    email = Column(String, unique=True, nullable=False, doc="Unique email address")
    password = Column(String, nullable=True, doc="Hashed password")
    name = Column(String(length=40), doc="User name")
    status = Column(
        Enum(constants.UserStatus),
        nullable=False,
        default=constants.UserStatus.MANAGER,
        create_type=False,
        doc="User status (manager or developer)",
    )
