__all__ = ['TestRun']
import datetime
import uuid

from pydantic import constr

from .base import Base


class TestRun(Base):
    id: uuid.UUID
    project_id: uuid.UUID | None = None
    start: datetime.datetime | None = None
    finish: datetime.datetime | None = None
    heartbeat: datetime.datetime | None = None
    keep_forever: bool | None = None
    sut_version: constr(strip_whitespace=True, max_length=128) | None = None
    sut_branch: constr(strip_whitespace=True, max_length=128) | None = None
    test_version: constr(strip_whitespace=True, max_length=128) | None = None
    test_branch: constr(strip_whitespace=True, max_length=128) | None = None
    properties: dict | None = None
    variant: dict | None = None
