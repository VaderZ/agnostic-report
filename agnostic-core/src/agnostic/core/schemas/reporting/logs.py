__all__ = ['TestRunLog', 'PagedTestRunLog']
import datetime
import uuid

from ..base import Base, Paginator


class TestRunLog(Base):
    id: uuid.UUID
    name: str | None = None
    start: datetime.datetime | None = None
    finish: datetime.datetime | None = None


class PagedTestRunLog(Paginator):
    data: list[TestRunLog]
