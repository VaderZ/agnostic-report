__all__ = ['Test', 'TestFinish']
import datetime
import uuid

from pydantic import constr

from .base import Base
from .lookups import TestResult


class Test(Base):
    id: uuid.UUID
    test_run_id: uuid.UUID | None = None
    start: datetime.datetime | None = None
    finish: datetime.datetime | None = None
    path: constr(strip_whitespace=True, max_length=512) | None = None
    name: constr(strip_whitespace=True, max_length=256) | None = None
    result: TestResult | None = None
    reason: str | None = None
    error_message: str | None = None
    description: str | None = None


class TestFinish(Test):
    result: TestResult
