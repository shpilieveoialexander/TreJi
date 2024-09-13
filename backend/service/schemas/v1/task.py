from pydantic import BaseModel, PositiveInt, constr

from db import constants

from .user import User


class CreateTask(BaseModel):
    name: constr(max_length=constants.MAX_NAME_LENGTH)
    description: constr(max_length=constants.MAX_DESCRIPTIONS_LENGTH)
    responsible_person_id: PositiveInt
    status: constants.TaskStatus
    priority: constants.Priority


class TaskResponse(BaseModel):
    name: str
    description: str
    priority_person: User
    created_by_person: User
    status: str
    priority: str

    class Config:
        from_attributes = True


class AssignResponse(BaseModel):
    task: TaskResponse
    assigned_user: User

    class Config:
        from_attributes = True
