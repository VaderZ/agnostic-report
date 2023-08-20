__all__ = [
    'Request', 'RequestCreate', 'RequestContents',
    'RequestType', 'RequestSQL', 'RequestHTTP',
    'RequestGRPC', 'RequestNATS'
]
import datetime
import uuid

from pydantic import Field, constr
from typing import Literal
from .base import Base
from .lookups import RequestType


class RequestContents(Base):
    request_type: RequestType


class RequestHTTP(RequestContents):
    request_type: Literal[RequestType.HTTP] = RequestType.HTTP
    code: int | None = None
    method: str
    url: str
    elapsed: float
    payload: str | None = None
    response: str | None = None
    timeout: bool | None = None


class RequestGRPC(RequestContents):
    request_type: Literal[RequestType.GRPC] = RequestType.GRPC
    method: str
    elapsed: float | None = None
    request: str
    response: str


class RequestSQL(RequestContents):
    request_type: Literal[RequestType.SQL] = RequestType.SQL
    query: str
    result: str
    elapsed: float


class RequestNATS(RequestContents):
    request_type: Literal[RequestType.NATS] = RequestType.NATS
    method: str
    subject: str
    payload: str


class Request(Base):
    id: uuid.UUID
    test_run_id: uuid.UUID | None = None
    test_id: uuid.UUID | None = None
    timestamp: datetime.datetime | None = None
    # request_type: RequestType | constr(strip_whitespace=True, max_length=128) | None = None
    contents: RequestHTTP | RequestGRPC | RequestSQL | RequestNATS | None = Field(None, discriminator='request_type')


class RequestCreate(Request):
    # request_type: RequestType | constr(strip_whitespace=True, max_length=128)
    id: uuid.UUID | None = None
    contents: RequestHTTP | RequestGRPC | RequestSQL | RequestNATS = Field(..., discriminator='request_type')
