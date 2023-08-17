__all__ = ['TestReport', 'TestsStatistics', 'PagedTests']
import datetime
import uuid

from ..base import Base, Paginator


class TestReport(Base):
    details: dict
    attachments: list[dict]
    logs: list[dict]
    metrics: list[dict]
    requests: list[dict]


class TestsStatistics(Base):
    id: uuid.UUID
    result: str | None = None
    name: str | None = None
    path: str | None = None
    execution_time: datetime.timedelta | None = None


class PagedTests(Paginator):
    data: list[TestsStatistics]
