from typing import List

from pydantic import (
    BaseModel,
    EmailStr
)


class EmailMessageEntity(BaseModel):
    to: List[EmailStr]
    subject: str
    content: str
