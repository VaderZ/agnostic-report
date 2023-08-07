import datetime

from pydantic import BaseModel

from .base import Base


class ProjectStatistics(Base):
    name: str | None
    test_runs_count: int | None
    latest_test_run: datetime.datetime | None


class PagedProjects(BaseModel):
    data: list[ProjectStatistics]
    count: int
    pages: int
    page: int
    page_size: int


class TestRunStatus(BaseModel):
    running: bool
    failed: bool
    terminated: bool


class TestRunsStatistics(Base):
    status: TestRunStatus | None
    variant: dict | None
    sut_branch: str | None
    sut_version: str | None
    test_branch: str | None
    test_version: str | None
    start: datetime.datetime | None
    finish: datetime.datetime | None
    heartbeat: datetime.datetime | None
    execution_time: datetime.timedelta | None
    tests_executed: int | None
    tests_failed: int | None
    properties: dict | None


class PagedTestRuns(BaseModel):
    data: list[TestRunsStatistics]
    count: int
    pages: int
    page: int
    page_size: int


class TestsOverTimeSeries(BaseModel):
    name: str
    data: list[int]

    class Config:
        orm_mode = True


class TestsOverTimeData(BaseModel):
    series: list[TestsOverTimeSeries]
    categories: list[datetime.datetime]


class TestsOverTime(BaseModel):
    data: TestsOverTimeData


class TestRunFiltersData(BaseModel):
    sut_branch: list[str | None]
    test_branch: list[str | None]
    variant: dict[str, list[str | None]]

    class Config:
        orm_mode = True


class TestRunFilters(BaseModel):
    data: TestRunFiltersData


class TopFailedTestsData(BaseModel):
    path: str
    name: str
    total: int
    failed: int
    percent_failed: int

    class Config:
        orm_mode = True


class TopFailedTests(BaseModel):
    data: list[TopFailedTestsData]


class MetricRequest(BaseModel):
    table: str
    name: str | None
    field: str | None
    func: str | None
    filter: str | None
    filter_field: str | None
    path: list[str] | None
    title: str


class MetricsData(BaseModel):
    name: str
    value: float| str | None


class MetricsAggregate(BaseModel):
    data: list[MetricsData]

    class Config:
        orm_mode = True


class TestsByResultData(BaseModel):
    series: list[int]
    labels: list[str | None]

    class Config:
        orm_mode = True


class TestsByResult(BaseModel):
    data: TestsByResultData


class TestsStatistics(Base):
    result: str | None
    name: str | None
    path: str | None
    execution_time: datetime.timedelta | None


class PagedTests(BaseModel):
    data: list[TestsStatistics]
    count: int
    pages: int
    page: int
    page_size: int


class TestRunMetricsListStatistics(Base):
    name: str | None
    value: str | None
    description: str | None


class PagedTestRunMetricsList(BaseModel):
    data: list[TestRunMetricsListStatistics]
    count: int
    pages: int
    page: int
    page_size: int


class TestRunProgressRecord(Base):
    level: str | None
    timestamp: datetime.datetime | None
    message: str | None
    details: str | None


class PagedTestRunProgressRecords(BaseModel):
    data: list[TestRunProgressRecord]
    count: int
    pages: int
    page: int
    page_size: int


class TestRunLog(Base):
    name: str | None
    start: datetime.datetime | None
    finish: datetime.datetime | None


class PagedTestRunLog(BaseModel):
    data: list[TestRunLog]
    count: int
    pages: int
    page: int
    page_size: int


class MetricOverTimeSeries(BaseModel):
    name: str
    data: list[float | None]

    class Config:
        orm_mode = True


class MetricOverTimeData(BaseModel):
    series: list[MetricOverTimeSeries]
    categories: list[datetime.datetime]


class MetricOverTimeReport(BaseModel):
    data: MetricOverTimeData | None


class TestReport(BaseModel):
    details: dict
    attachments: list[dict]
    logs: list[dict]
    metrics: list[dict]
    requests: list[dict]

    class Config:
        orm_mode = True
