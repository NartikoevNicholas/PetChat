import datetime

from uuid import UUID

from typing import Optional

from pydantic import (
    BaseModel,
    ConfigDict
)


class UserHistoryEntity(BaseModel):
    model_config = ConfigDict(from_attributes=True)
    id: Optional[UUID] = None
    user_id: Optional[UUID] = None
    update_field: Optional[str] = None
    old_value: Optional[str] = None
    new_value: Optional[str] = None
    dt_update: Optional[datetime.datetime] = None
    dt_created: Optional[datetime.datetime] = None


class UserHistoryCreateEntity(BaseModel):
    user_id: UUID
    update_field: str
    old_value: str
    new_value: str
