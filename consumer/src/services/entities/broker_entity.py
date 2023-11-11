from pydantic import (
    BaseModel,
    EmailStr
)


class BrokerUserEmailEntity(BaseModel):
    username: str
    email: EmailStr
    link: str
