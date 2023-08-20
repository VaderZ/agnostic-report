__all__ = ['ProjectStatistics', 'PagedProjects']
import datetime
import uuid

from ..base import Base, Paginator


class ProjectStatistics(Base):
    id: uuid.UUID
    name: str | None = None
    test_runs_count: int | None = None
    latest_test_run: datetime.datetime | None = None


class PagedProjects(Paginator):
    data: list[ProjectStatistics]
