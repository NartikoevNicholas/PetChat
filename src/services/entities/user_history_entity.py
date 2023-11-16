import datetime
import typing as tp
from uuid import UUID

from pydantic import (
    BaseModel,
    ConfigDict
)


class UserHistory(BaseModel):
    model_config = ConfigDict(from_attributes=True)
    id: tp.Optional[UUID] = None
    user_id: tp.Optional[UUID] = None
    update_field: tp.Optional[str] = None
    old_value: tp.Optional[str] = None
    new_value: tp.Optional[str] = None
    dt_update: tp.Optional[datetime.datetime] = None
    dt_created: tp.Optional[datetime.datetime] = None


class UserHistoryDTO(BaseModel):
    user_id: UUID
    update_field: str
    old_value: str
    new_value: str
