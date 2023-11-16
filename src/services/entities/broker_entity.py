from pydantic import (
    BaseModel,
    EmailStr
)


class BrokerUserEmail(BaseModel):
    username: str
    email: EmailStr
    link: str
