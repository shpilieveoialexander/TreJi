from fastapi import APIRouter, Depends, HTTPException, status
from fastapi.responses import UJSONResponse
from sqlalchemy import select

from db import constants, models
from db.session import DBSession
from service.core import settings
from service.core.celery_app import celery_app
from service.core.dependencies import (get_current_manager, get_refresh_token,
                                       get_session)
from service.core.security import (create_jwt_token, create_tmp_token,
                                   hash_password, validate_tmp_token,
                                   verify_password)
from service.schemas import v1 as schemas_v1

router = APIRouter()


@router.post(
    "/manager-sign-up/",
    status_code=status.HTTP_201_CREATED,
    response_model=schemas_v1.JWTTokensResponse,
)
async def manager_sign_up(
    form_data: schemas_v1.ManagerAuth = Depends(),
    session: DBSession = Depends(get_session),
) -> UJSONResponse:
    """
    Manager User sign up\n
    Sign Up User. Return User\n
    Responses:\n
    `201` CREATED - Everything is good (SUCCESS Response)\n
    `400` BAD_REQUEST - User with this email exists\n
    `422` UNPROCESSABLE_ENTITY - Failed field validation\n
    """
    # Checking existing email
    exists_query = select(models.User).filter_by(email=form_data.email)
    with session() as db:
        email_exists = db.execute(select(exists_query.exists())).scalar()
    if email_exists:
        raise HTTPException(
            status_code=status.HTTP_409_CONFLICT,
            detail=f"User with email {form_data.email} exists",
        )
    # Create new user
    user = models.User(
        email=form_data.email,
        password=hash_password(form_data.password),
        name=form_data.name,
    )
    with session() as db:
        db.add(user)
        db.commit()
        db.refresh(user)
    # Return JWT tokens
    return UJSONResponse(
        status_code=status.HTTP_201_CREATED,
        content={
            "access_token": create_jwt_token(user.id),
            "refresh_token": create_jwt_token(
                user.id, jwt_type=constants.JWTType.REFRESH
            ),
            "token_type": "Bearer",
            "access_token_lifetime": settings.JWT_ACCESS_TOKEN_EXPIRE_MINUTES,
            "refresh_token_lifetime": settings.JWT_REFRESH_TOKEN_EXPIRE_MINUTES,
        },
    )


@router.post(
    "/developer-invitation/",
    response_model=schemas_v1.MsgResponse,
)
async def invite_developer(
    input_data: schemas_v1.DeveloperInvite,
    session: DBSession = Depends(get_session),
    current_manager: models.User = Depends(get_current_manager),
):
    """
    Send  Invitation to developer sign up\n
    Sign Up User. Return User\n
    Responses:\n
    `200` OK - Everything is good (SUCCESS Response)\n
    `400` BAD_REQUEST - User with this email exists\n
    `403` Forbidden - User hasn't got access\n
    `422` UNPROCESSABLE_ENTITY - Failed field validation\n
    """
    # Checking existing email
    exists_query = select(models.User).filter_by(email=input_data.email)
    with session() as db:
        email_exists = db.execute(select(exists_query.exists())).scalar()
    if email_exists:
        raise HTTPException(
            status_code=status.HTTP_409_CONFLICT,
            detail=f"User with email {input_data.email} exists",
        )
    user = models.User(
        name=input_data.name,
        email=input_data.email,
        status=constants.UserStatus.DEVELOPER,
    )
    with session() as db:
        db.add(user)
        db.commit()
        db.refresh(user)

    tmp_token = create_tmp_token(pk=user.id)
    celery_app.send_task(
        "service.tasks.delay.send_invite",
        args=[input_data.email, tmp_token],
    )
    return UJSONResponse(content={"msg": f"We have sent invite to {input_data.email}"})


@router.post(
    "/developer-sign-up/",
    status_code=status.HTTP_201_CREATED,
    response_model=schemas_v1.JWTTokensResponse,
)
async def developer_sign_up(
    form_data: schemas_v1.DeveloperAuth = Depends(),
    session: DBSession = Depends(get_session),
) -> UJSONResponse:
    """
    Developer User sign up\n
    Sign Up User. Return User\n
    Responses:\n
    `201` CREATED - Everything is good (SUCCESS Response)\n
    `404` NOT_FOUND - Group not found\n
    `409` CONFLICT - User with this email does not exists\n
    `422` UNPROCESSABLE_ENTITY - Failed field validation\n
    """
    user_id = validate_tmp_token(form_data.token)
    with session() as db:
        user = db.get(models.User, user_id)
    if not user:
        raise HTTPException(
            status_code=status.HTTP_409_CONFLICT,
            detail=f"User does not exists or token expired",
        )
    user.password = hash_password(form_data.password)
    with session() as db:
        db.add(user)
        db.commit()
        db.refresh(user)

    return UJSONResponse(
        status_code=status.HTTP_201_CREATED,
        content={
            "access_token": create_jwt_token(user.id),
            "refresh_token": create_jwt_token(
                user.id, jwt_type=constants.JWTType.REFRESH
            ),
            "token_type": "Bearer",
            "access_token_lifetime": settings.JWT_ACCESS_TOKEN_EXPIRE_MINUTES,
            "refresh_token_lifetime": settings.JWT_REFRESH_TOKEN_EXPIRE_MINUTES,
        },
    )


@router.post("/access-token/", response_model=schemas_v1.JWTTokensResponse)
async def login(
    form_data: schemas_v1.Auth = Depends(), session: DBSession = Depends(get_session)
) -> UJSONResponse:
    """
    Login\n
    Obtain email and password, and return access and refresh tokens for future requests\n
    Responses:\n
    `200` OK - Everything is good (SUCCESS Response)\n
    `403` FORBIDDEN - Invalid password\n
    `404` NOT_FOUND - User is inactive or not found\n
    `422` UNPROCESSABLE_ENTITY - Failed field validation\n
    """
    # Get user
    user_query = select(models.User).filter_by(email=form_data.email)
    with session() as db:
        user = db.execute(user_query).scalar_one_or_none()
    if not user:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND, detail="User not found"
        )
    # Verify password
    if not verify_password(form_data.password, user.password):
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN, detail="Invalid credentials"
        )
    return UJSONResponse(
        status_code=status.HTTP_200_OK,
        content={
            "access_token": create_jwt_token(user.id),
            "refresh_token": create_jwt_token(
                user.id, jwt_type=constants.JWTType.REFRESH
            ),
            "token_type": "Bearer",
            "access_token_lifetime": settings.JWT_ACCESS_TOKEN_EXPIRE_MINUTES,
            "refresh_token_lifetime": settings.JWT_REFRESH_TOKEN_EXPIRE_MINUTES,
        },
    )


@router.post("/refresh-token/", response_model=schemas_v1.JWTTokensResponse)
async def refresh_token(
    token_data: schemas_v1.JWTTokenPayload = Depends(get_refresh_token),
    session: DBSession = Depends(get_session),
) -> UJSONResponse:
    """
    Refresh token\n
    Obtain refresh token  return access tokens and refresh token\n
    Responses:\n
    `200` OK - Everything is good (SUCCESS Response)\n
    `401` UNAUTHORIZED - Not authenticated\n
    `403` FORBIDDEN - Could not validate credentials\n
    `404` NOT_FOUND - User is inactive or not found\n
    """
    # Checking existing user
    user_query = select(models.User).filter_by(id=token_data.pk)
    with session() as db:
        user_exists = db.execute(select(user_query.exists())).scalar()

    if not user_exists:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="User blocked or not found",
        )
    # Return new JWT tokens
    return UJSONResponse(
        status_code=status.HTTP_200_OK,
        content={
            "access_token": create_jwt_token(token_data.pk),
            "refresh_token": create_jwt_token(
                token_data.pk, jwt_type=constants.JWTType.REFRESH
            ),
            "token_type": "Bearer",
            "access_token_lifetime": settings.JWT_ACCESS_TOKEN_EXPIRE_MINUTES,
            "refresh_token_lifetime": settings.JWT_REFRESH_TOKEN_EXPIRE_MINUTES,
        },
    )
