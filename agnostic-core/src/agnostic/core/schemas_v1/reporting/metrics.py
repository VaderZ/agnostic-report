__all__ = [
    'MetricRequest', 'MetricsData', 'MetricsAggregate',
    'TestRunMetricsListStatistics', 'PagedTestRunMetricsList'
]
from ..base import Base, Paginator


class MetricRequest(Base):
    table: str
    name: str | None = None
    field: str | None = None
    func: str | None = None
    filter: str | None = None
    filter_field: str | None = None
    path: list[str] | None = None
    title: str


class MetricsData(Base):
    name: str
    value: float| str | None = None


class MetricsAggregate(Base):
    data: list[MetricsData]


class TestRunMetricsListStatistics(Base):
    name: str | None = None
    value: float | None = None
    description: str | None = None


class PagedTestRunMetricsList(Paginator):
    data: list[TestRunMetricsListStatistics]
