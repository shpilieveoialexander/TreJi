from fastapi import Depends, HTTPException, status
from jose import jwt

from db import constants, models
from db.session import DBSession
from service.core import settings
from service.schemas import v1 as schemas_v1

from .redis_cache import redis_cache
from .security import APIKeyHeader


def get_session() -> DBSession:
    """Return DB session and close after using"""
    return DBSession


async def get_jwt_token(
    token: str = Depends(APIKeyHeader(name="Authorization")),
) -> schemas_v1.JWTTokenPayload:
    """Get JWT access or refresh token"""
    if redis_cache.get(token):
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN,
            detail="You have used blocked JWT token",
        )
    try:
        payload = jwt.decode(
            token, settings.SECRET_KEY, algorithms=[settings.HASH_ALGORITHM]
        )
        return schemas_v1.JWTTokenPayload(pk=payload["pk"], type=payload["type"])
    except (jwt.JWTError, KeyError):
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN,
            detail="Could not validate credentials",
        )


async def get_access_token(
    token_data: schemas_v1.JWTTokenPayload = Depends(get_jwt_token),
) -> schemas_v1.JWTTokenPayload:
    """Check JWT access token"""
    if token_data.type != constants.JWTType.ACCESS.value:
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN,
            detail="This is not a valid JWT access token",
        )
    return token_data


async def get_refresh_token(
    token_data: schemas_v1.JWTTokenPayload = Depends(get_jwt_token),
) -> schemas_v1.JWTTokenPayload:
    """heck JWT refresh token"""
    if token_data.type != constants.JWTType.REFRESH.value:
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN,
            detail="This is not a valid JWT refresh token",
        )
    return token_data


async def get_current_user(
    session: DBSession = Depends(get_session),
    token_payload: schemas_v1.JWTTokenPayload = Depends(get_access_token),
) -> models.User:
    """Return current user instance"""
    user_query = models.User.get_one(id=token_payload.pk, is_active=True)
    with session() as db:
        user = db.scalars(user_query).one_or_none()
    if not user:
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN,
            detail="Could not validate credentials",
        )
    return user
