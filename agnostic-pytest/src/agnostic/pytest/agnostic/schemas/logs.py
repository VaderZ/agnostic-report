__all__ = ['Log', 'LogCreate']
import datetime
import uuid

from pydantic import constr

from .base import Base


class Log(Base):
    id: uuid.UUID
    test_run_id: uuid.UUID | None = None
    test_id: uuid.UUID | None = None
    name: constr(strip_whitespace=True, max_length=256) | None = None
    start: datetime.datetime | None = None
    finish: datetime.datetime | None = None
    body: str | None = None


class LogCreate(Log):
    id: uuid.UUID | None = None
    name: constr(strip_whitespace=True, max_length=256)
