import typing as tp

from pydantic import (
    BaseModel,
    EmailStr
)


class EmailMessage(BaseModel):
    to: tp.List[EmailStr]
    subject: str
    content: str
