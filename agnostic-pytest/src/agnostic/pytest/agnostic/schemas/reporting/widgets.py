__all__ = [
    'TestsOverTimeSeries', 'TestsOverTimeData', 'TestsOverTime',
    'TopFailedTestsData', 'TopFailedTests', 'TestsByResultData',
    'TestsByResult'
]
import datetime

from ..base import Base


class TestsOverTimeSeries(Base):
    name: str
    data: list[int]


class TestsOverTimeData(Base):
    series: list[TestsOverTimeSeries]
    categories: list[datetime.datetime]


class TestsOverTime(Base):
    data: TestsOverTimeData


class TopFailedTestsData(Base):
    path: str
    name: str
    total: int
    failed: int
    percent_failed: int


class TopFailedTests(Base):
    data: list[TopFailedTestsData]


class TestsByResultData(Base):
    series: list[int]
    labels: list[str | None]


class TestsByResult(Base):
    data: TestsByResultData
