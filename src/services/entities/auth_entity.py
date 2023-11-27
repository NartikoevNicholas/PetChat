from datetime import datetime
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
    access = 'access_token'
    refresh = 'refresh_token'


class JWTPayload(BaseModel):
    model_config = ConfigDict(use_enum_values=True)

    user_id: UUID
    type: JWTTypeToken
    exp: datetime
    iat: float

    def model_payload(self) -> dict:
        data = self.model_dump()
        data['user_id'] = data['user_id'].hex
        return data
