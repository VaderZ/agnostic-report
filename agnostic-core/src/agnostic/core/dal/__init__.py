from ..session import async_session
from .attachments import Attachments
from .exceptions import DALException, DuplicateError, ForeignKeyError, NotFoundError
from .logs import Logs
from .metrics import Metrics
from .metrics_ot import MetricsOverTime
from .progress import Progress
from .projects import Projects
from .reporting import Reporting
from .requests import Requests
from .test_runs import TestRuns
from .tests import Tests


async def get_projects():
    async with async_session() as session:
        yield Projects(session)


async def get_test_runs():
    async with async_session() as session:
        yield TestRuns(session)


async def get_tests():
    async with async_session() as session:
        yield Tests(session)


async def get_logs():
    async with async_session() as session:
        yield Logs(session)


async def get_metrics():
    async with async_session() as session:
        yield Metrics(session)


async def get_progress():
    async with async_session() as session:
        yield Progress(session)


async def get_requests():
    async with async_session() as session:
        yield Requests(session)


async def get_metrics_ot():
    async with async_session() as session:
        yield MetricsOverTime(session)


async def get_attachments():
    async with async_session() as session:
        yield Attachments(session)


async def get_reporting():
    async with async_session() as session:
        yield Reporting(session)
