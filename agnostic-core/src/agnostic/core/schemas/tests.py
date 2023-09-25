__all__ = ["TestPatch", "TestUpdate", "TestCreate", "Test", "Tests", "TestStart", "TestFinish"]
import datetime
import uuid

from pydantic import Field
from pydantic import constr

from .base import Base, BaseRoot, Timestamp
from .lookups import TestResult


class TestPatch(Base):
    start: datetime.datetime | None = None
    finish: datetime.datetime | None = None
    path: constr(strip_whitespace=True, max_length=512) | None = None
    name: constr(strip_whitespace=True, max_length=256) | None = None
    result: TestResult | None = None
    reason: str | None = None
    error_message: str | None = None
    description: str | None = None


class TestUpdate(TestPatch):
    start: datetime.datetime
    path: constr(strip_whitespace=True, max_length=512)
    name: constr(strip_whitespace=True, max_length=256)


class TestCreate(TestUpdate):
    id: uuid.UUID | None = Field(default_factory=uuid.uuid4)
    test_run_id: uuid.UUID | None = None


class Test(TestCreate):
    id: uuid.UUID
    test_run_id: uuid.UUID


class Tests(BaseRoot):
    root: list[Test]


class TestStart(Base):
    id: uuid.UUID | None = None
    test_run_id: uuid.UUID | None = None
    start: datetime.datetime | None = None
    path: constr(strip_whitespace=True, max_length=512)
    name: constr(strip_whitespace=True, max_length=256)


class TestFinish(Base):
    id: uuid.UUID | None = None
    test_run_id: uuid.UUID | None = None
    finish: datetime.datetime | None = None
    result: TestResult
