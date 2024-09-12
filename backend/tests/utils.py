from db import constants
from service.core.security import create_jwt_token


def get_headers(user_id: int) -> dict[str, str]:
    """Create and return headers for future auth"""
    access_token = create_jwt_token(user_id)
    return {"Authorization": f"Bearer {access_token}"}


def get_refresh_headers(user_id: int) -> dict[str, str]:
    """Create and return headers for refresh token tests"""
    refresh_token = create_jwt_token(user_id, jwt_type=constants.JWTType.REFRESH)
    return {"Authorization": f"Bearer {refresh_token}"}
