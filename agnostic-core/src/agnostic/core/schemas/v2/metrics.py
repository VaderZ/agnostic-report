__all__ = ["MetricPatch", "MetricUpdate", "MetricCreate", "Metric", "Metrics"]
import datetime
import decimal
import uuid

from pydantic import constr, Field, model_validator

from .base import Base, BaseRoot


class MetricPatch(Base):
    timestamp: datetime.datetime | None = None
    name: constr(strip_whitespace=True, max_length=256) | None = None
    value: decimal.Decimal | None = None
    description: str | None = None


class MetricUpdate(MetricPatch):
    timestamp: datetime.datetime
    name: constr(strip_whitespace=True, max_length=256)
    value: decimal.Decimal


class MetricCreate(MetricUpdate):
    id: uuid.UUID | None = Field(default_factory=uuid.uuid4)
    test_run_id: uuid.UUID
    test_id: uuid.UUID | None = None


class Metric(MetricCreate):
    id: uuid.UUID
    formatted: str

    @model_validator(mode="before")
    @classmethod
    def format_description(cls, values):
        if values.description:
            values.formatted = values.description.format(values.value)
        else:
            values.formatted = ""
        return values


class Metrics(BaseRoot):
    root: list[Metric]
