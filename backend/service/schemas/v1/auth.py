from fastapi import Form
from fastapi.exceptions import ValidationException
from pydantic import BaseModel, EmailStr, constr

from db import constants


class ManagerAuth:
    def __init__(
        self,
        name: str = Form(
            ..., min_length=constants.NAME_MIN, max_length=constants.NAME_MAX
        ),
        email: EmailStr = Form(...),
        password: str = Form(
            ..., min_length=constants.PASSWORD_MIN, max_length=constants.PASSWORD_MAX
        ),
        password_confirm: str = Form(
            ..., min_length=constants.PASSWORD_MIN, max_length=constants.PASSWORD_MAX
        ),
    ):
        if password != password_confirm:
            raise ValidationException("Password missmatch")
        self.email = email
        self.password = password
        self.name = name


class DeveloperInvite(BaseModel):
    name: constr(min_length=constants.NAME_MIN, max_length=constants.NAME_MAX)
    email: EmailStr


class DeveloperAuth:
    def __init__(
        self,
        token: str = Form(...),
        password: str = Form(
            ..., min_length=constants.PASSWORD_MIN, max_length=constants.PASSWORD_MAX
        ),
        password_confirm: str = Form(
            ..., min_length=constants.PASSWORD_MIN, max_length=constants.PASSWORD_MAX
        ),
    ):
        if password != password_confirm:
            raise ValidationException("Password missmatch")
        self.token = token
        self.password = password


class Auth:
    def __init__(
        self,
        email: EmailStr = Form(...),
        password: str = Form(
            ..., min_length=constants.PASSWORD_MIN, max_length=constants.PASSWORD_MAX
        ),
    ):
        self.email = email
        self.password = password
