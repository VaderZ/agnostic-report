__all__ = [
    "Base",
    "BaseRoot",
    "CRUDCollection",
    "Timestamp",
    "KeyValue",
    "NameValue",
    "StringValue",
]
import datetime
import typing

from pydantic import BaseModel, RootModel, ConfigDict, Field


class Base(BaseModel):
    model_config = ConfigDict(from_attributes=True, validate_assignment=True)


class BaseRoot(RootModel):
    model_config = ConfigDict(from_attributes=True, validate_assignment=True)

    def __iter__(self):
        return iter(self.root)

    def __getitem__(self, item):
        return self.root[item]


class CRUDCollection(Base):
    count: int
    items: BaseRoot


class Timestamp(Base):
    timestamp: datetime.datetime | None = Field(
        default_factory=lambda: datetime.datetime.now(datetime.UTC)
    )


class KeyValue(Base):
    key: str
    value: typing.Any


class NameValue(Base):
    name: str
    value: typing.Any


class StringValue(Base):
    value: str
