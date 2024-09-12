from datetime import datetime

from pydantic import BaseModel, EmailStr, PositiveInt

from db import constants


class User(BaseModel):
    id: PositiveInt
    name: str
    email: EmailStr
    created_at: datetime
    status: constants.UserStatus

    class Config:
        use_enum_values = True
        from_attributes = True
