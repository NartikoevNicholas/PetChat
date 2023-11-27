import datetime
from uuid import UUID
from typing import Optional

from pydantic import (
    BaseModel,
    EmailStr,
    Field,
    ConfigDict,
)

min_len_username = 8
max_len_username = 100

min_len_pass = 8
max_len_pass = 100


class UserDTO(BaseModel):
    model_config = ConfigDict(from_attributes=True, loc_by_alias=False)

    id: Optional[UUID] = Field(
        default=None
    )
    username: Optional[str] = Field(
        default=None,
        min_length=min_len_username,
        max_length=max_len_pass
    )
    email: Optional[EmailStr] = Field(
        default=None
    )
    hashed_password: Optional[str] = Field(
        default=None,
        min_length=min_len_pass,
        max_length=max_len_pass
    )
    is_active: Optional[bool] = Field(
        default=None
    )
    is_deleted: Optional[bool] = Field(
        default=None
    )
    is_superuser: Optional[bool] = Field(
        default=None
    )
    dt_update: Optional[datetime.datetime] = Field(
        default=None
    )
    dt_created: Optional[datetime.datetime] = Field(
        default=None
    )


class UserEmailDTO(BaseModel):
    email: EmailStr


class UserUsernameDTO(BaseModel):
    username: str = Field(
        min_length=min_len_username,
        max_length=max_len_pass
    )


class UserPasswordDTO(BaseModel):
    password: str = Field(
        min_length=min_len_pass,
        max_length=max_len_pass
    )


class UserEmailPasswordDTO(UserEmailDTO, UserPasswordDTO):
    pass


class UserUsernamePasswordDTO(UserUsernameDTO, UserPasswordDTO):
    pass


class UserRequestDTO(UserEmailDTO, UserUsernameDTO):
    hashed_password: str = Field(
        alias='password',
        min_length=min_len_pass,
        max_length=max_len_pass
    )
    is_superuser: Optional[bool] = Field(
        default=False
    )


class UserResponseDTO(UserEmailDTO, UserUsernameDTO):
    id: UUID
    is_superuser: bool


class UserUpdatePassword(BaseModel):
    new_password: str = Field(
        min_length=min_len_pass,
        max_length=max_len_pass
    )
    password: str = Field(
        min_length=min_len_pass,
        max_length=max_len_pass
    )
