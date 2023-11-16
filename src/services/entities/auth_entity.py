import datetime as dt
from uuid import UUID
from enum import Enum

from pydantic import (
    BaseModel,
    field_validator,
    ConfigDict
)


class JWTToken(BaseModel):
    access_token: str
    refresh_token: str


class JWTRefreshToken(BaseModel):
    refresh_token: str


class JWTTypeToken(str, Enum):
    access = 'access'
    refresh = 'refresh'


class JWTPayload(BaseModel):
    model_config = ConfigDict(use_enum_values=True)

    user_id: UUID
    token_type: JWTTypeToken
    exp: dt.datetime

    @field_validator('user_id')
    def check_user_id(cls, val):
        return val.hex
