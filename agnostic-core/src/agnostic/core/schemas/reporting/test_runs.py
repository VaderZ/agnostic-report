__all__ = [
    'TestRunStatus', 'TestRunsStatistics', 'PagedTestRuns',
    'TestRunFiltersData', 'TestRunFilters'
]
import datetime
import uuid

from ..base import Base, Paginator


class TestRunStatus(Base):
    running: bool
    failed: bool
    terminated: bool


class TestRunsStatistics(Base):
    id: uuid.UUID
    status: TestRunStatus | None = None
    variant: dict | None = None
    sut_branch: str | None = None
    sut_version: str | None = None
    test_branch: str | None = None
    test_version: str | None = None
    start: datetime.datetime | None = None
    finish: datetime.datetime | None = None
    heartbeat: datetime.datetime | None = None
    execution_time: datetime.timedelta | None = None
    tests_executed: int | None = None
    tests_failed: int | None = None
    properties: dict | None = None


class PagedTestRuns(Paginator):
    data: list[TestRunsStatistics]


class TestRunFiltersData(Base):
    sut_branch: list[str | None]
    test_branch: list[str | None]
    variant: dict[str, list[str | None]]


class TestRunFilters(Base):
    data: TestRunFiltersData
