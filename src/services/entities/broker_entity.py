from pydantic import (
    BaseModel,
    EmailStr
)


class BrokerUserReg(BaseModel):
    username: str
    email: EmailStr
    link: str


class BrokerUserEmailUpdate(BaseModel):
    email: EmailStr
    link: str
