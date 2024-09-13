from enum import Enum

MAX_NAME_LENGTH = 40
MAX_DESCRIPTIONS_LENGTH = 180


class Priority(Enum):
    HIGH = "High"
    MEDIUM = "Medium"
    LOW = "Low"


class TaskStatus(Enum):
    TODO = "Todo"
    IN_PROGRESS = "InProgress"
    DONE = "Done"
