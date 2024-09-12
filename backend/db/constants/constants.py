from enum import Enum


class UserStatus(Enum):
    MANAGER = "Manager"
    DEVELOPER = "Developer"


PASSWORD_MIN = 8
PASSWORD_MAX = 150

NAME_MIN = 8
NAME_MAX = 50
