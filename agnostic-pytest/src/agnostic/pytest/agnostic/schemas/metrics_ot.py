__all__ = ['MetricOverTime', 'MetricOverTimeCreate']
import datetime
import uuid

from pydantic import constr

from .base import Base


class MetricOverTime(Base):
    id: uuid.UUID
    test_run_id: uuid.UUID | None = None
    test_id: uuid.UUID | None = None
    timestamp: datetime.datetime | None
    name: constr(strip_whitespace=True, max_length=128)
    values: dict


class MetricOverTimeCreate(MetricOverTime):
    id: uuid.UUID | None = None
    timestamp: datetime.datetime | None = None
