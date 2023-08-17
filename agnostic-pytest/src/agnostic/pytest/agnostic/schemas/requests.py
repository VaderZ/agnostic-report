__all__ = [
    'Request', 'RequestCreate', 'RequestContents',
    'RequestType', 'RequestSQL', 'RequestHTTP',
    'RequestGRPC', 'RequestNATS'
]
import datetime
import uuid

from pydantic import Field, constr

from .base import Base
from .lookups import RequestType


class Request(Base):
    id: uuid.UUID
    test_run_id: uuid.UUID | None = None
    test_id: uuid.UUID | None = None
    timestamp: datetime.datetime | None = None
    request_type: RequestType | constr(strip_whitespace=True, max_length=128) | None = None
    contents: dict | None = Field(None, exclude={'request_type'})


class RequestCreate(Request):
    request_type: RequestType | constr(strip_whitespace=True, max_length=128)
    contents: dict = Field(..., exclude={'request_type'})


class RequestContents(Base):
    request_type: RequestType


class RequestHTTP(RequestContents):
    request_type: RequestType = RequestType.HTTP
    code: int | None = None
    method: str
    url: str
    elapsed: float
    payload: str | None = None
    response: str | None = None
    timeout: bool | None = None


class RequestGRPC(RequestContents):
    request_type: RequestType = RequestType.GRPC
    method: str
    elapsed: float | None = None
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
    