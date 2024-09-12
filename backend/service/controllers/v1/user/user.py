from fastapi import APIRouter, Depends
from fastapi_pagination import Page
from fastapi_pagination.ext.sqlalchemy import paginate
from sqlalchemy import select

from db import constants, models
from db.session import DBSession
from service.core.dependencies import (get_access_token, get_current_user,
                                       get_session)
from service.schemas import v1 as schemas_v1

router = APIRouter()


@router.get("/me/", response_model=schemas_v1.User)
async def user_me(
    token_payload: schemas_v1.JWTTokenPayload = Depends(get_access_token),
    session: DBSession = Depends(get_session),
    user: models.User = Depends(get_current_user),
) -> models.User:
    """
    Return User me info\n
    Responses:\n
    `200` OK - Everything is good (SUCCESS Response)\n
    `401` UNAUTHORIZED - You have not provided authorization token\n
    `403` FORBIDDEN - Invalid authorization\n
    `422` UNPROCESSABLE_ENTITY - Failed field validation\n
    """
    return user


@router.get("/managers/", response_model=Page[schemas_v1.User])
def get_managers(
    session: DBSession = Depends(get_session),
    user: models.User = Depends(get_current_user),
) -> models.User:
    """
    Return Managers users info\n
    Responses:\n
    `200` OK - Everything is good (SUCCESS Response)\n
    `401` UNAUTHORIZED - You have not provided authorization token\n
    `403` FORBIDDEN - Invalid authorization\n
    `422` UNPROCESSABLE_ENTITY - Failed field validation\n
    """
    managers_query = select(models.User).where(
        models.User.status == constants.UserStatus.MANAGER
    )
    with session() as db:
        return paginate(db, managers_query)


@router.get("/developers/", response_model=Page[schemas_v1.User])
async def get_developers(
    session: DBSession = Depends(get_session),
    user: models.User = Depends(get_current_user),
) -> models.User:
    """
    Return Developers users info\n
    Responses:\n
    `200` OK - Everything is good (SUCCESS Response)\n
    `401` UNAUTHORIZED - You have not provided authorization token\n
    `403` FORBIDDEN - Invalid authorization\n
    `422` UNPROCESSABLE_ENTITY - Failed field validation\n
    """
    managers_query = select(models.User).where(
        models.User.status == constants.UserStatus.DEVELOPER
    )
    with session() as db:
        return paginate(db, managers_query)
