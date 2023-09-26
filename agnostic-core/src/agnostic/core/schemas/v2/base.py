__all__ = ["Base", "BaseRoot", "Timestamp", "KeyValue", "StringValue"]
import datetime
import typing

from pydantic import BaseModel, RootModel, ConfigDict


class Base(BaseModel):
    model_config = ConfigDict(from_attributes=True, validate_assignment=True)


class BaseRoot(RootModel):
    model_config = ConfigDict(from_attributes=True, validate_assignment=True)

    def __iter__(self):
        return iter(self.root)

    def __getitem__(self, item):
        return self.root[item]


class Timestamp(BaseModel):
    timestamp: datetime.datetime | None


class KeyValue(BaseModel):
    key: str
    value: typing.Any


class StringValue(BaseModel):
    value: str
