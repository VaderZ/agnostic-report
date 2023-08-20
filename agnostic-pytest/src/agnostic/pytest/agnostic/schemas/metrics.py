__all__ = ['Metric', 'MetricCreate']
import datetime
import decimal
import uuid

from pydantic import constr

from .base import Base


class Metric(Base):
    id: uuid.UUID
    test_run_id: uuid.UUID | None = None
    test_id: uuid.UUID | None = None
    timestamp: datetime.datetime | None = None
    name: constr(strip_whitespace=True, max_length=256) | None = None
    value: decimal.Decimal | None = None
    description: str | None = None


class MetricCreate(Metric):
    id: uuid.UUID | None = None
    name: constr(strip_whitespace=True, max_length=256)
