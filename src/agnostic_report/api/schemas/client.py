import datetime
from decimal import Decimal
from enum import Enum
from typing import Any
from uuid import UUID

from pydantic import BaseModel, constr, Field

from .base import Base


class TestResult(str, Enum):
    PASSED = 'passed'
    FAILED = 'failed'
    SKIPPED = 'skipped'
    XPASSED = 'xpassed'
    XFAILED = 'xfailed'


class Level(str, Enum):
    DEBUG = 'DEBUG'
    INFO = 'INFO'
    WARNING = 'WARNING'
    ERROR = 'ERROR'


class RequestType(str, Enum):
    HTTP = 'http'
    GRPC = 'grpc'
    SQL = 'sql'
    NATS = 'nats'


class Timestamp(BaseModel):
    timestamp: datetime.datetime | None


class KeyValue(BaseModel):
    key: str
    value: Any


class StringValue(BaseModel):
    value: str


class Project(Base):
    name: str | None
    config: dict | None


class ProjectCreate(Project):
    name: str


class TestRun(Base):
    project_id: UUID | None
    start: datetime.datetime | None
    finish: datetime.datetime | None
    heartbeat: datetime.datetime | None
    keep_forever: bool | None
    sut_version: constr(strip_whitespace=True, max_length=128) | None
    sut_branch: constr(strip_whitespace=True, max_length=128) | None
    test_version: constr(strip_whitespace=True, max_length=128) | None
    test_branch: constr(strip_whitespace=True, max_length=128)  | None
    properties: dict | None
    variant: dict | None


class Test(Base):
    test_run_id: UUID | None
    start: datetime.datetime | None
    finish: datetime.datetime | None
    path: constr(strip_whitespace=True, max_length=512) | None
    name: constr(strip_whitespace=True, max_length=256) | None
    result: TestResult | None
    reason: str | None
    error_message: str | None
    description: str | None


class TestFinish(Test):
    result: TestResult


class Log(Base):
    test_run_id: UUID | None
    test_id: UUID | None
    name: constr(strip_whitespace=True, max_length=256) | None
    start: datetime.datetime | None
    finish: datetime.datetime | None
    body: str | None


class LogCreate(Log):
    name: constr(strip_whitespace=True, max_length=256)


class Metric(Base):
    test_run_id: UUID | None
    test_id: UUID | None
    timestamp: datetime.datetime | None
    name: constr(strip_whitespace=True, max_length=256) | None
    value: Decimal | None
    description: str | None


class MetricCreate(Metric):
    name: constr(strip_whitespace=True, max_length=256)


class Progress(Base):
    test_run_id: UUID | None
    test_id: UUID | None
    timestamp: datetime.datetime | None
    level: Level | None
    message: str | None
    details: str | None


class ProgressCreate(Progress):
    level: constr(strip_whitespace=True, max_length=10)
    message: str


class Request(Base):
    test_run_id: UUID | None
    test_id: UUID | None
    timestamp: datetime.datetime | None
    request_type: RequestType | constr(strip_whitespace=True, max_length=128) | None
    contents: dict | None = Field(..., exclude={'request_type'})


class RequestCreate(Request):
    request_type: RequestType | constr(strip_whitespace=True, max_length=128)
    contents: dict = Field(..., exclude={'request_type'})


class RequestContents(BaseModel):
    request_type: RequestType


class RequestHTTP(RequestContents):
    request_type: RequestType = RequestType.HTTP
    code: int | None
    method: str
    url: str
    elapsed: float
    payload: str | None
    response: str | None
    timeout: bool | None


class RequestGRPC(RequestContents):
    request_type: RequestType = RequestType.GRPC
    method: str
    elapsed: float | None
    request: str
    response: str


class RequestSQL(RequestContents):
    request_type: RequestType = RequestType.SQL
    query: str
    result: str
    elapsed: float


class RequestNATS(RequestContents):
    request_type: RequestType = RequestType.NATS
    method: str
    subject: str
    payload: str


class MetricOverTime(Base):
    test_run_id: UUID | None
    test_id: UUID | None
    timestamp: datetime.datetime | None
    name: constr(strip_whitespace=True, max_length=128)
    values: dict


class Attachment(Base):
    test_run_id: UUID | None
    test_id: UUID | None
    timestamp: datetime.datetime | None
    name: constr(strip_whitespace=True, max_length=512)
    mime_type: constr(strip_whitespace=True, max_length=128)
    size: int | None
    content: bytes


class AttachmentCreate(Attachment):
    name: constr(strip_whitespace=True, max_length=512)
    mime_type: constr(strip_whitespace=True, max_length=128)
    size: int | None
    content: bytes
