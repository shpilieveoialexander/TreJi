from sqlalchemy import (VARCHAR, Column, ForeignKey, Integer, String,
                        UniqueConstraint)
from sqlalchemy.orm import Mapped, relationship

from db import constants

from .base import BaseModel
from .user import User


class TaskExecutors(BaseModel):
    """Task executors"""

    __tablename__ = "task_executors"
    user_id = Column(
        Integer,
        ForeignKey("user.id", ondelete="CASCADE"),
        nullable=False,
        doc="Executor  id",
    )
    task_id = Column(
        Integer,
        ForeignKey("task.id", ondelete="CASCADE"),
        nullable=False,
        doc="Executor  id",
    )
    assigned_user = relationship(User, lazy="joined", foreign_keys=[user_id])

    task = relationship("Task", lazy="joined", foreign_keys=[task_id])

    __table_args__ = (UniqueConstraint("user_id", "task_id"),)


class Task(BaseModel):
    """Task table"""

    __tablename__ = "task"
    name = Column(
        String(length=constants.MAX_NAME_LENGTH), nullable=False, doc="Task name"
    )
    description = Column(
        String(length=constants.MAX_DESCRIPTIONS_LENGTH),
        nullable=False,
        doc="Task description",
    )
    responsible_person_id = Column(
        Integer,
        ForeignKey("user.id", ondelete="CASCADE"),
        nullable=False,
        doc="responsible  person id",
    )
    priority = Column(
        VARCHAR,
        nullable=False,
        default=constants.Priority.HIGH,
        doc="Priority status value",
    )
    status = Column(
        VARCHAR,
        nullable=False,
        default=constants.TaskStatus.TODO,
        doc="Task status value",
    )
    created_by = Column(
        Integer,
        ForeignKey("user.id", ondelete="CASCADE"),
        nullable=False,
        doc="Created by person id",
    )
    priority_person: Mapped[User] = relationship(
        User, uselist=False, lazy="joined", foreign_keys=[responsible_person_id]
    )
    created_by_person: Mapped[User] = relationship(
        User, uselist=False, lazy="joined", foreign_keys=[created_by]
    )
