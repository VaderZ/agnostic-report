__all__ = ['TestRunProgressRecord', 'PagedTestRunProgressRecords']
import datetime
import uuid

from ..base import Base, Paginator


class TestRunProgressRecord(Base):
    id: uuid.UUID
    level: str | None = None
    timestamp: datetime.datetime | None = None
    message: str | None = None
    details: str | None = None


class PagedTestRunProgressRecords(Paginator):
    data: list[TestRunProgressRecord]
