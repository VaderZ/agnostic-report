__all__ = ['MetricOverTime']
import datetime
import uuid

from pydantic import constr

from .base import Base


class MetricOverTime(Base):
    id: uuid.UUID
    test_run_id: uuid.UUID | None
    test_id: uuid.UUID | None
    timestamp: datetime.datetime | None
    name: constr(strip_whitespace=True, max_length=128)
    values: dict
