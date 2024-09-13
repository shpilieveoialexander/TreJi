from db import constants, models

from .base import BaseFactory
from .utils import fake


class TaskFactory(BaseFactory):
    name = fake.name()
    description = fake.name()
    priority = constants.Priority.LOW.value
    status = constants.TaskStatus.TODO.value

    class Meta:
        model = models.Task


class TaskExecutors(BaseFactory):
    class Meta:
        model = models.TaskExecutors
