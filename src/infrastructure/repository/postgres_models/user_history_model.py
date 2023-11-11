from sqlalchemy import (
    UUID,
    ForeignKey
)

from sqlalchemy.orm import (
    Mapped,
    mapped_column
)

from .abstract_model import AbstractBase


class UserHistory(AbstractBase):
    __tablename__ = 'user_history'

    user_id = mapped_column(
        UUID,
        ForeignKey('user.id'),
        nullable=True,
        doc='user id who was updated'
    )
    update_field: Mapped[str]
    old_value: Mapped[str]
    new_value: Mapped[str]
