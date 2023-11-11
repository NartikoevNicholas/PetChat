from sqlalchemy import (
    UUID,
    TIMESTAMP,
)
from sqlalchemy.sql import func
from sqlalchemy.orm import (
    mapped_column,
    DeclarativeBase
)


class Base(DeclarativeBase):
    pass


class AbstractBase(Base):
    __abstract__ = True

    id = mapped_column(
        UUID,
        primary_key=True,
        server_default=func.gen_random_uuid(),
        unique=True,
        nullable=False,
        doc='Unique id of the string in table'
    )
    dt_update = mapped_column(
        TIMESTAMP(timezone=True),
        nullable=False,
        server_default=func.now(),
        server_onupdate=func.now(),
        doc='Date and time the entry was updated'
    )
    dt_created = mapped_column(
        TIMESTAMP(timezone=True),
        nullable=False,
        server_default=func.now(),
        doc='Date and time the entry was created',
    )
