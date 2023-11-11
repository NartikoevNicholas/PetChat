from sqlalchemy import (
    TEXT,
    BOOLEAN,
)
from sqlalchemy.orm import (
    Mapped,
    mapped_column
)
from sqlalchemy.dialects.postgresql import CITEXT

from .abstract_model import AbstractBase


class User(AbstractBase):
    __tablename__ = 'user'

    username = mapped_column(
        CITEXT(length=50),
        unique=True,
        nullable=False,
        doc='user username'
    )
    email = mapped_column(
        CITEXT(length=150),
        unique=True,
        nullable=False,
        doc='user email'
    )
    hashed_password = mapped_column(
        TEXT,
        nullable=False,
        doc='user hashed password'
    )
    is_active = mapped_column(
        BOOLEAN,
        nullable=False,
        default=False,
        doc="If true then the email is confirmed"
    )
    is_deleted = mapped_column(
        BOOLEAN,
        nullable=False,
        default=False,
        doc="If true then the user is deleted your account"
    )
    is_superuser: Mapped[bool]
