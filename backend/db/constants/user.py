from enum import Enum


class JWTType(str, Enum):
    """JWT token types"""

    ACCESS = "access"
    REFRESH = "refresh"
