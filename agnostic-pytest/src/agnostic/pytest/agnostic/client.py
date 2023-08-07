import abc
import datetime
import mimetypes
import os
import uuid
from decimal import Decimal
from io import BufferedReader
from typing import Any
from uuid import UUID, uuid4

import redis
import requests

from . import schemas


class Context:

    @property
    def base_url(self) -> str:
        return self.get_key('base_url')

    @base_url.setter
    def base_url(self, value: str):
        self.set_key('base_url', value)

    @property
    def project_id(self) -> UUID | None:
        try:
            return UUID(self.get_key('project'))
        except (ValueError, TypeError):
            return None

    @project_id.setter
    def project_id(self, value: UUID | str):
        self.set_key('project', str(value))

    @property
    def test_run_id(self) -> UUID | None:
        try:
            return UUID(self.get_key('test_run_id'))
        except (ValueError, TypeError):
            return None

    @test_run_id.setter
    def test_run_id(self, value: UUID | str):
        self.set_key('test_run_id', str(value))

    @property
    def test_id(self) -> UUID | None:
        try:
            return uuid.UUID(self.get_key('test_id'))
        except TypeError:
            return None

    @test_id.setter
    def test_id(self, value: UUID | str):
        self.set_key('test_id', str(value))

    @property
    def test_start(self) -> datetime.datetime | None:
        try:
            return datetime.datetime.fromisoformat(self.get_key('test_start'))
        except TypeError:
            return None

    @test_start.setter
    def test_start(self, value: UUID | str):
        self.set_key('test_start', str(value))

    @property
    def test_finish(self) -> datetime.datetime | None:
        try:
            return datetime.datetime.fromisoformat(self.get_key('test_finish'))
        except TypeError:
            None

    @test_finish.setter
    def test_finish(self, value: datetime.datetime):
        self.set_key('test_finish', str(value))

    @property
    def log_marker(self) -> str:
        return self.get_key('log_marker')

    @log_marker.setter
    def log_marker(self, value: str):
        self.set_key('log_marker', value)

    @property
    def test_run_failed(self) -> bool:
        value = self.get_key('test_run_failed')
        if value is None:
            return False
        return bool(int(value))

    @test_run_failed.setter
    def test_run_failed(self, value: bool):
        self.set_key('test_run_failed', str(int(value)))

    @property
    def offline(self) -> bool:
        value = self.get_key('offline')
        if value is None:
            return False
        return bool(int(value))

    @offline.setter
    def offline(self, value: bool):
        self.set_key('offline', str(int(value)))

    @abc.abstractmethod
    def set_key(self, key: str, value: Any):
        ...

    @abc.abstractmethod
    def get_key(self, item: str) -> Any:
        ...


_local_context = {}


class LocalContext(Context):

    def __init__(self, store: dict | None = None):
        if not store:
            self.store = _local_context
        else:
            self.store = store

    def set_key(self, key, value):
        self.store[key] = value

    def get_key(self, item):
        return self.store.get(item)


class RedisContext(Context):

    def __init__(self, host: str, port: int = 6379, db: int = 0):
        self.redis = redis.Redis(host=host, port=port, db=db)

    def set_key(self, key, value):
        self.redis.set(key, value.encode('ascii'))

    def get_key(self, item):
        value = self.redis.get(item)
        return value.decode('ascii') if value is not None else None


class HTTPClient:

    def __init__(self, ctx: Context):
        self.ctx = ctx

    @property
    def base_url(self):
        return f'{self.ctx.base_url}/projects/{self.ctx.project_id}'

    @abc.abstractmethod
    def get(self, path: str):
        ...

    @abc.abstractmethod
    def post(self, path: str, data: str | dict = '{}'):
        ...

    @abc.abstractmethod
    def post_files(self, path: str, files: dict):
        ...

    @abc.abstractmethod
    def put(self, path: str, data: str | dict = '{}'):
        ...

    @abc.abstractmethod
    def patch(self, path: str, data: str | dict = '{}'):
        ...


class LocalHTTPClient(HTTPClient):

    def __init__(self, ctx: Context):
        super(LocalHTTPClient, self).__init__(ctx)
        self.headers = {'Content-Type': 'application/json'}
        self.session = requests.Session()

    def get(self, path: str):
        if not self.ctx.offline:
            return self.session.get(f'{self.base_url}{path}')

    def post(self, path: str, data: str | dict = '{}'):
        if not self.ctx.offline:
            result = self.session.post(f'{self.base_url}{path}', data=data, headers=self.headers)
            return result

    def post_files(self, path: str, files: dict):
        if not self.ctx.offline:
            return self.session.post(f'{self.base_url}{path}', files=files)

    def put(self, path: str, data: str | dict = '{}'):
        if not self.ctx.offline:
            return self.session.put(f'{self.base_url}{path}', data=data, headers=self.headers)

    def patch(self, path: str, data: str | dict = '{}'):
        if not self.ctx.offline:
            return self.session.patch(f'{self.base_url}{path}', data=data, headers=self.headers)


class Client:
    Level = schemas.Level
    TestResult = schemas.TestResult
    RequestType = schemas.RequestType
    RequestHTTP = schemas.RequestHTTP
    RequestGRPC = schemas.RequestGRPC
    RequestNATS = schemas.RequestNATS
    RequestSQL = schemas.RequestSQL

    def __init__(self, ctx: Context, http_client: type = LocalHTTPClient):
        self.ctx = ctx
        self.http = http_client(self.ctx)

    def set_log_marker(self, name: str):
        self.ctx.log_marker = name

    def get_log_marker(self) -> str:
        return self.ctx.log_marker

    @property
    def is_test_run_active(self):
        return self.ctx.test_run_id is not None

    @property
    def test_run_path(self):
        if not self.ctx.test_run_id:
            raise RuntimeError('Test run ID is not specified. Is test run started?')
        return f'/test-runs/{self.ctx.test_run_id}'

    @property
    def test_path(self):
        if not self.ctx.test_run_id:
            raise RuntimeError('Test run ID is not specified. Is test run started?')
        elif not self.ctx.test_id:
            raise RuntimeError('Test ID is not specified. Is test started?')
        return f'{self.test_run_path}/tests/{self.ctx.test_id}'

    def get_test_path(self, test_id: UUID | None):
        if test_id:
            return f'{self.test_run_path}/tests/{test_id}'
        return self.test_path

    def start_test_run(self, sut_version: str = None, sut_branch: str = None,
                       test_version: str = None, test_branch: str = None,
                       variant: dict[str, str] = None, properties: dict[str, Any] = None):
        if not self.ctx.test_run_id:
            self.ctx.test_run_id = uuid4()
        else:
            test_run = self.http.get(f'{self.test_run_path}')
            if test_run.ok:
                return self.ctx.test_run_id
        data = schemas.TestRun(
            id=self.ctx.test_run_id,
            project_id=self.ctx.project_id,
            **locals()
        )
        self.http.post(f'/test-runs', data.json(exclude_unset=True))
        return self.ctx.test_run_id

    def finish_test_run(self):
        data = schemas.TestRun(
            id=self.ctx.test_run_id,
            project_id=self.ctx.project_id
        )
        self.http.post(f'{self.test_run_path}/finish', data.json(exclude_unset=True))
        self.ctx.test_run_id = None

    def test_run_heartbeat(self):
        data = schemas.TestRun(
            id=self.ctx.test_run_id,
            project_id=self.ctx.project_id
        )
        self.http.post(f'{self.test_run_path}/heartbeat', data.json(exclude_unset=True))

    def set_test_run_property(self, key: str, value: str):
        data = schemas.KeyValue(
            id=self.ctx.test_run_id,
            project_id=self.ctx.project_id,
            **locals()
        )
        self.http.post(f'{self.test_run_path}/property', data.json(exclude_unset=True))

    def start_test(self, name: str, path: str, description: str = None):
        self.ctx.test_id = uuid4()
        self.ctx.test_start = datetime.datetime.utcnow()
        data = schemas.Test(
            id=self.ctx.test_id,
            test_run_id=self.ctx.test_run_id,
            **locals()
        )
        self.http.post(f'{self.test_run_path}/tests', data.json(exclude_unset=True))

    def finish_test(self, result: schemas.TestResult, reason: str = None,
                    error_message: str = None, test_id: UUID | None = None):
        test_id = test_id or self.ctx.test_id
        self.ctx.test_finish = datetime.datetime.utcnow()
        if result == schemas.TestResult.FAILED:
            self.ctx.test_run_failed = True
        data = schemas.Test(
            id=test_id,
            test_run_id=self.ctx.test_run_id,
            **locals()
        )
        self.http.post(f'{self.get_test_path(test_id)}/finish', data.json(exclude_unset=True))

    def add_test_metric(self, name: str, value: Decimal, description: str = None, test_id: UUID | None = None):
        test_id = test_id or self.ctx.test_id
        data = schemas.Metric(
            test_run_id=self.ctx.test_run_id,
            **locals()
        )
        self.http.post(f'{self.get_test_path(test_id)}/metrics', data.json(exclude_unset=True))

    def add_test_run_metric(self, name: str, value: Decimal, description: str = None):
        data = schemas.Metric(
            test_id=self.ctx.test_id,
            test_run_id=self.ctx.test_run_id,
            **locals()
        )
        self.http.post(f'{self.test_run_path}/metrics', data.json(exclude_unset=True))

    def add_test_run_log(self, name: str, body: str,
                         start: datetime.datetime = None, finish: datetime.datetime = None) -> UUID:
        log_id = uuid4()
        data = schemas.LogCreate(
            id=log_id,
            test_run_id=self.ctx.test_run_id,
            **locals()
        )
        self.http.post(f'{self.test_run_path}/logs', data.json(exclude_unset=True))
        return log_id

    def append_test_run_log(self, log_id: UUID, body: str):
        data = schemas.StringValue(
            value=body
        )
        self.http.patch(f'{self.test_run_path}/logs/{log_id}/body', data.json(exclude_unset=True))

    def add_test_log(self, name: str, body: str, start: datetime.datetime = None,
                     finish: datetime.datetime = None, test_id: UUID | None = None) -> UUID:
        test_id = test_id or self.ctx.test_id
        log_id = uuid4()
        data = schemas.LogCreate(
            id=log_id,
            test_run_id=self.ctx.test_run_id,
            **locals()
        )
        self.http.post(f'{self.get_test_path(test_id)}/logs', data.json(exclude_unset=True))
        return log_id

    def append_test_log(self, log_id, body: str, test_id: UUID | None = None):
        test_id = test_id or self.ctx.test_id
        data = schemas.StringValue(
            value=body
        )
        self.http.patch(f'{self.get_test_path(test_id)}/logs/{log_id}/body', data.json(exclude_unset=True))

    def add_request(self, contents: schemas.RequestContents, timestamp: datetime.datetime | None = None,
                    test_id: UUID | None = None):
        test_id = test_id or self.ctx.test_id
        data = schemas.Request(
            test_run_id=self.ctx.test_run_id,
            test_id=test_id,
            timestamp=timestamp if timestamp else datetime.datetime.utcnow(),
            request_type=contents.request_type,
            contents=contents
        )
        # Requests might be logged at setup phase while they do not belong to a certain test
        try:
            self.http.post(f'{self.get_test_path(test_id)}/requests', data.json(exclude_unset=True))
        except RuntimeError:
            self.http.post(f'{self.test_run_path}/requests', data.json(exclude_unset=True))

    def add_metric_over_time(self, name: str, values: dict, test_id: UUID | None = None):
        data = schemas.MetricOverTime(
            test_run_id=self.ctx.test_run_id,
            test_id=test_id or self.ctx.test_id,
            name=name,
            values=values
        )
        self.http.post(f'{self.test_run_path}/metrics-ot', data.json(exclude_unset=True))

    def add_progress(self, level: schemas.Level, message: str,
                     details: str | None = None, test_id: UUID | None = None):
        data = schemas.Progress(
            test_run_id=self.ctx.test_run_id,
            test_id=test_id or self.ctx.test_id,
            level=level,
            message=message,
            details=details
        )
        self.http.post(f'{self.test_run_path}/progress', data.json(exclude_unset=True))

    def info(self, message: str, details: str | None = None, test_id: UUID | None = None):
        self.add_progress(self.Level.INFO, message, details, test_id)

    def warning(self, message: str, details: str | None = None, test_id: UUID | None = None):
        self.add_progress(self.Level.WARNING, message, details, test_id)

    def error(self, message: str, details: str | None = None, test_id: UUID | None = None):
        self.add_progress(self.Level.ERROR, message, details, test_id)

    def __add_attachment(self, base_url: str, attachment: str | BufferedReader,
                         name: str | None = None, mime_type: str | None = None):
        if isinstance(attachment, str):
            content = open(attachment, 'rb')
            name = os.path.basename(attachment) if not name else name
            mime_type = mimetypes.guess_type(attachment)[0] if not mime_type else mime_type
        else:
            if not name or not mime_type:
                raise RuntimeError('Name and MIME type have to be specified for file buffer')
            content = attachment

        self.http.post_files(f'{base_url}/attachments', files={'attachment': (name, content, mime_type)})

    def add_test_run_attachment(self, attachment: str | BufferedReader,
                                name: str | None = None, mime_type: str | None = None):
        self.__add_attachment(self.test_run_path, attachment, name, mime_type)

    def add_test_attachment(self, attachment: str | BufferedReader, name: str | None = None,
                            mime_type: str | None = None, test_id: UUID | None = None):
        self.__add_attachment(self.get_test_path(test_id), attachment, name, mime_type)


_client = None


def get_client(ctx: Context = None, http_client: type = LocalHTTPClient):
    global _client
    if not _client and ctx:
        _client = Client(ctx, http_client)
    return _client
