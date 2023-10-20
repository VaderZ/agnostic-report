from agnostic.core.session import async_session
from .exceptions import CRUDException, DuplicateError, ForeignKeyError, NotFoundError
from .logs import Logs
from .metrics import Metrics
from .progress import Progress
from .projects import Projects
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


async def get_metrics():
    async with async_session() as session:
        yield Metrics(session)


async def get_progress():
    async with async_session() as session:
        yield Progress(session)


async def get_logs():
    async with async_session() as session:
        yield Logs(session)
