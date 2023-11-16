import datetime
import typing as tp
from uuid import UUID

from pydantic import (
    BaseModel,
    EmailStr,
    Field,
    ConfigDict,
    field_validator
)

from src.core.config import get_config


settings = get_config()


class User(BaseModel):
    model_config = ConfigDict(from_attributes=True)

    id: tp.Optional[UUID] = None
    username: tp.Optional[str] = None
    email: tp.Optional[EmailStr] = None
    hashed_password: tp.Optional[str] = None
    is_active: tp.Optional[bool] = None
    is_deleted: tp.Optional[bool] = None
    is_superuser: tp.Optional[bool] = None
    dt_update: tp.Optional[datetime.datetime] = None
    dt_created: tp.Optional[datetime.datetime] = None


class UserEmail(BaseModel):
    email: EmailStr = Field(min_length=8, max_length=39)


class UserUsername(BaseModel):
    username: str = Field(min_length=8, max_length=39)


class UserCredEmail(UserEmail):
    password: str = Field(min_length=8, max_length=39)


class UserCredUsername(UserUsername):
    password: str = Field(min_length=8, max_length=39)


class UserDTO(UserEmail, UserUsername):
    hashed_password: str = Field(alias='password', min_length=8, max_length=39)
    is_superuser: bool

    @field_validator('hashed_password')
    def check_hashed_password(cls, value):
        return settings.pwd_context().hash(value)
