__all__ = ["LogPatch", "LogUpdate", "LogCreate", "Log", "Logs"]
import datetime
import uuid

from pydantic import constr, Field

from .base import Base, BaseRoot


class LogPatch(Base):
    name: constr(strip_whitespace=True, max_length=256) | None = None
    start: datetime.datetime | None = None
    finish: datetime.datetime | None = None
    body: str | None = ""


class LogUpdate(LogPatch):
    name: constr(strip_whitespace=True, max_length=256)


class LogCreate(LogUpdate):
    id: uuid.UUID | None = Field(default_factory=uuid.uuid4)
    test_run_id: uuid.UUID
    test_id: uuid.UUID | None = None


class Log(LogCreate):
    id: uuid.UUID


class Logs(BaseRoot):
    root: list[Log]
