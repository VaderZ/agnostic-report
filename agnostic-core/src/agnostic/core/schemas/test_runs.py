__all__ = ["TestRunUpdate", "TestRunCreate", "TestRun", "TestRuns"]
import datetime
import uuid

from pydantic import constr, Field

from .base import Base, BaseRoot


class TestRunUpdate(Base):
    start: datetime.datetime | None = None
    finish: datetime.datetime | None = None
    heartbeat: datetime.datetime | None = None
    keep_forever: bool | None = None
    sut_version: constr(strip_whitespace=True, max_length=128) | None = None
    sut_branch: constr(strip_whitespace=True, max_length=128) | None = None
    test_version: constr(strip_whitespace=True, max_length=128) | None = None
    test_branch: constr(strip_whitespace=True, max_length=128) | None = None
    properties: dict | None = {}
    variant: dict | None = {}


class TestRunCreate(TestRunUpdate):
    id: uuid.UUID | None = Field(default_factory=uuid.uuid4)
    project_id: uuid.UUID | None = None


class TestRun(TestRunCreate):
    id: uuid.UUID
    project_id: uuid.UUID


class TestRuns(BaseRoot):
    root: list[TestRun]
