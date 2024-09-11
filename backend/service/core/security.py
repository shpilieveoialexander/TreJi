import base64
from datetime import datetime, timedelta
from string import ascii_letters
from typing import Final, Optional

from fastapi import HTTPException, Request, status
from fastapi.openapi.models import APIKey, APIKeyIn
from fastapi.security.api_key import APIKeyBase
from jose import jwt
from passlib.context import CryptContext

from db.constants import JWTType
from service.core import settings

HASH_ALGORITHM: Final[str] = "HS256"
pwd_context = CryptContext(schemes=["bcrypt"], deprecated="auto")


def create_jwt_token(pk: int | str, jwt_type: JWTType = JWTType.ACCESS) -> str:
    """
    Create access JWT token for login into the system
    """
    expired_times: dict = {
        JWTType.ACCESS.value: settings.JWT_ACCESS_TOKEN_EXPIRE_MINUTES,
        JWTType.REFRESH.value: settings.JWT_REFRESH_TOKEN_EXPIRE_MINUTES,
    }
    expire = datetime.utcnow() + timedelta(
        minutes=expired_times.get(
            jwt_type.value, settings.JWT_ACCESS_TOKEN_EXPIRE_MINUTES
        )
    )
    to_encode = {
        "pk": str(pk),
        "exp": expire,
        "type": jwt_type.value,
    }
    encoded_jwt = jwt.encode(
        to_encode, settings.SECRET_KEY, algorithm=settings.HASH_ALGORITHM
    )
    return encoded_jwt


class APIKeyHeader(APIKeyBase):
    def __init__(
        self,
        *,
        name: str,
        scheme_name: Optional[str] = None,
        description: Optional[str] = None,
        auto_error: bool = True,
    ):
        self.model: APIKey = APIKey(
            **{"in": APIKeyIn.header}, name=name, description=description
        )
        self.scheme_name = scheme_name or self.__class__.__name__
        self.auto_error = auto_error

    async def __call__(self, request: Request) -> Optional[str]:
        api_key = request.headers.get(self.model.name)
        if not api_key:
            if self.auto_error:
                raise HTTPException(
                    status_code=status.HTTP_401_UNAUTHORIZED, detail="Not authenticated"
                )
            else:
                return None
        return api_key.split(" ")[-1]


def verify_password(password: str, hashed_password: str) -> bool:
    """Verify the provided password against the hashed password"""
    return pwd_context.verify(password, hashed_password)


def hash_password(password: str) -> str:
    """Create and return hashed password."""
    return pwd_context.hash(password)


def create_tmp_token(pk: int | str, exp: float = settings.TMP_TOKEN_LIFETIME) -> str:
    """
    Generate and return token

    Token generation algorithm:
    1) Obtain pk and create string like 'pk:timestamp';
    2) Encode this string with base64;
    3) Find equal letters in encoded string and SECRET_KEY.
       Take index of these letters and take letters from alphabet by these index;
    5) Replace letter from encoded string by letter from alphabet
       and index from SECRET_KEY
    6) If changes will be more than 25%, stop replacing
    """
    timestamp = int((datetime.utcnow() + timedelta(minutes=exp)).timestamp())
    data = f"{pk}:{timestamp}"
    enc_str = base64.urlsafe_b64encode(bytes(data, encoding="utf8")).decode()
    enc_list = []
    changes = 0
    for char in enc_str:
        if char in settings.SECRET_KEY and changes < len(enc_str) / 4:
            try:
                index = settings.SECRET_KEY.index(char)
                enc_list.append(f"{index}{ascii_letters[index]}")
                changes += 1
            except IndexError:
                enc_list.append(char)
        else:
            enc_list.append(char)
    token = "".join(enc_list)
    if "=" in token:
        c = token.count("=")
        token = token.replace("=" * c, f"c{c}")
    return token


def decode_token(token):
    for i, char in enumerate(settings.SECRET_KEY):
        if i > len(ascii_letters) - 1:
            break
        if f"{i}{ascii_letters[i]}" in token:
            token = token.replace(f"{i}{ascii_letters[i]}", char)
    if token[-1].isdigit() and token[-2] == "c":
        token = token.replace(f"c{token[-1]}", "=" * int(token[-1]))
    return token


def validate_tmp_token(token: str) -> str | None:
    """
    Check token and return True or False

    Token validation algorithm:
    1) Replace token with SECRET_KEY letters
    2) Decode result
    3) Take timestamp value and check is time'sUp
    4) Return True if all alright and False if something went wrong
    """
    encoded_token = decode_token(token=token)
    try:
        data = base64.urlsafe_b64decode(bytes(encoded_token, "utf-8")).decode()
        pk, created_at = data.split(":")
        if datetime.utcnow().timestamp() < int(created_at):
            return pk
        return
    except ValueError:
        return
