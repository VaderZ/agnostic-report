import datetime
from uuid import UUID, uuid4

from sqlalchemy.exc import IntegrityError
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy.future import select
from sqlalchemy.sql.expression import update

from agnostic.core import models, schemas
from .exceptions import DuplicateError, ForeignKeyError, NotFoundError, InvalidArgumentsError


class Progress:
    def __init__(self, session: AsyncSession):
        self.session = session

    async def get(self, id: UUID) -> schemas.Progress:
        progress = (
            await self.session.execute(
                select(models.Progress)
                .where(models.Progress.id == id)
            )
        ).scalar()

        if not progress:
            raise NotFoundError(f'Progress record {id} does not exist')

        return schemas.Progress.from_orm(progress)

    async def get_all(self, test_run_id: UUID | None = None, test_id: UUID | None = None) -> [schemas.Progress]:
        if not test_run_id and not test_id:
            raise InvalidArgumentsError('Test Run and/or Test id have to be provided')

        query = select(models.Progress)

        if test_run_id:
            query = query.where(models.Progress.test_run_id == test_run_id)

        if test_id:
            query = query.where(models.Progress.test_id == test_id)

        progresses = (await self.session.execute(query)).scalars().all()

        return [schemas.Progress.from_orm(progress) for progress in progresses]

    async def create(self, progress: schemas.ProgressCreate) -> UUID:
        progress.id = progress.id or uuid4()
        progress.timestamp = progress.timestamp or datetime.datetime.utcnow()
        progress = models.Progress(**progress.dict())
        self.session.add(progress)

        try:
            await self.session.commit()
        except IntegrityError as e:
            if 'foreign key constraint' in e.orig.args[0]:
                raise ForeignKeyError(f'Test Run {progress.test_run_id} or Test {progress.test_id} does not exist')
            else:
                raise DuplicateError(f'Progress record {progress.id} already exists')

        return progress.id

    async def update(self, progress: schemas.Progress, exclude_unset: bool = False) -> UUID:
        try:
            result = (
                await self.session.execute(
                    update(models.Progress)
                    .where(models.Progress.id == progress.id)
                    .values(**progress.dict(exclude_unset=exclude_unset))
                )
            )
        except IntegrityError:
            raise NotFoundError(f'Test Run {progress.test_run_id} or Test {progress.test_id} does not exist')

        if result.rowcount < 1:
            raise NotFoundError(f'Progress record {progress.id} does not exist')

        await self.session.commit()

        return progress.id
