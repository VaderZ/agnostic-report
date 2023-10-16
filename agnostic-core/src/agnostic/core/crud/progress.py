import datetime
import uuid

from sqlalchemy.exc import IntegrityError
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy.sql.expression import select, update, and_, func

from agnostic.core import models as m
from agnostic.core.schemas import v2 as s
from .exceptions import DuplicateError, ForeignKeyError, NotFoundError


class Progress:
    def __init__(self, session: AsyncSession):
        self.session = session

    async def get(self, id_: uuid.UUID) -> s.Progress:
        progress = (
            await self.session.execute(select(m.Progress).where(m.Progress.id == id_))
        ).scalar()

        if not progress:
            raise NotFoundError(f"Progress {id_} does not exist")

        return s.Progress.model_validate(progress)

    async def get_all(
        self,
        test_run_id: uuid.UUID | None,
        test_id: uuid.UUID | None,
        page: int = 1,
        page_size: int = 100,
    ) -> s.CRUDCollection:
        where = []
        if test_run_id:
            where.append(m.Progress.test_run_id == test_run_id)
        if test_id:
            where.append(m.Progress.test_id == test_id)
        count = (
            await self.session.execute(select(func.count(m.Progress.id)).where(and_(*where)))
        ).scalar()
        progresses = (
            (
                await self.session.execute(
                    select(m.Progress)
                    .where(and_(*where))
                    .order_by(m.Progress.timestamp.desc())
                    .offset(page_size * (page - 1))
                    .limit(page_size)
                )
            )
            .scalars()
            .all()
        )

        return s.CRUDCollection(items=s.Progresses.model_validate(progresses), count=count)

    async def create(self, progress: s.ProgressCreate) -> uuid.UUID:
        progress.id = progress.id or uuid.uuid4()
        progress.timestamp = progress.timestamp or datetime.datetime.now(datetime.UTC)
        self.session.add(m.Progress(**progress.model_dump()))

        try:
            await self.session.commit()
        except IntegrityError as e:
            if "foreign key constraint" in e.orig.args[0]:
                raise ForeignKeyError(f"Test Run {progress.test_run_id} does not exist")
            else:
                raise DuplicateError(f"Progress record {progress.id} already exists")

        return progress.id

    async def update(
        self,
        id_: uuid.UUID,
        progress: s.ProgressUpdate | s.ProgressPatch,
        exclude_unset: bool = False,
    ) -> uuid.UUID:
        try:
            result = await self.session.execute(
                update(m.Progress)
                .where(m.Progress.id == id_)
                .values(**progress.model_dump(exclude_unset=exclude_unset))
            )
        except IntegrityError:
            raise NotFoundError(f"Test Run {progress.test_run_id} does not exist")

        if result.rowcount < 1:
            raise NotFoundError(f"Progress record {progress.id} does not exist")

        await self.session.commit()

        return id_
