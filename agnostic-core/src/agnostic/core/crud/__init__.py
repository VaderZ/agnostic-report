from agnostic.core.session import async_session
from .projects import Projects
from .exceptions import CRUDException, DuplicateError, ForeignKeyError, NotFoundError


async def get_projects():
    async with async_session() as session:
        yield Projects(session)
