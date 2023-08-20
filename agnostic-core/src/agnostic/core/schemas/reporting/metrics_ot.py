__all__ = ['MetricOverTimeSeries', 'MetricOverTimeData', 'MetricOverTimeReport']
import datetime

from ..base import Base


class MetricOverTimeSeries(Base):
    name: str
    data: list[float | None]


class MetricOverTimeData(Base):
    series: list[MetricOverTimeSeries]
    categories: list[datetime.datetime]


class MetricOverTimeReport(Base):
    data: MetricOverTimeData | None = None
