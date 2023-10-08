__all__ = ['TestPatch', 'TestUpdate', 'TestCreate', 'Test', 'Tests', 'TestOutcome']
import datetime
import uuid

from pydantic import constr, Field

from .base import Base, BaseRoot
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
    ...


class TestCreate(TestUpdate):
    id: uuid.UUID | None = Field(default_factory=uuid.uuid4)
    test_run_id: uuid.UUID


class Test(TestCreate):
    ...


class Tests(BaseRoot):
    root: list[Test]


class TestOutcome(Base):
    timestamp: datetime.datetime | None = None
    result: TestResult
    reason: str | None = None
    error_message: str | None = None
