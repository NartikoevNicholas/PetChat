import datetime

from uuid import UUID

from typing import Optional

from pydantic import (
    BaseModel,
    EmailStr,
    Field,
    ConfigDict
)


class UserEntity(BaseModel):
    model_config = ConfigDict(from_attributes=True)

    id: Optional[UUID] = None
    username: Optional[str] = None
    email: Optional[EmailStr] = None
    hashed_password: Optional[str] = None
    is_active: Optional[bool] = None
    is_deleted: Optional[bool] = None
    is_superuser: Optional[bool] = None
    dt_update: Optional[datetime.datetime] = None
    dt_created: Optional[datetime.datetime] = None


class UserCreateEntity(BaseModel):
    username: str = Field(min_length=8, max_length=39)
    email: EmailStr
    hashed_password: str = Field(alias='password')
    is_superuser: bool
