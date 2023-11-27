import typing as tp

from pydantic import (
    BaseModel,
    EmailStr
)


class BrokerUserEmail(BaseModel):
    username: str
    email: EmailStr
    link: str


class BrokerUserEmailUpdate(BaseModel):
    email: EmailStr
    link: str


class BrokerFunctions(BaseModel):
    send_registration_email_func: tp.Callable
    send_update_email_func: tp.Callable
