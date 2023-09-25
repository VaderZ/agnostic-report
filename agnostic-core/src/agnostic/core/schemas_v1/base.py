__all__ = ['Base', 'Timestamp', 'KeyValue', 'StringValue', 'Paginator']

import datetime
import typing

from pydantic import BaseModel, ConfigDict


class Base(BaseModel):
    model_config = ConfigDict(
        from_attributes=True,
        validate_assignment=True
    )


class Timestamp(BaseModel):
    timestamp: datetime.datetime | None


class KeyValue(BaseModel):
    key: str
    value: typing.Any


class StringValue(BaseModel):
    value: str


class Paginator(Base):
    data: list[Base]
    count: int
    pages: int
    page: int
    page_size: int
