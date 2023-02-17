import datetime
from uuid import UUID, uuid4

from sqlalchemy import func
from sqlalchemy.exc import IntegrityError
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy.future import select
from sqlalchemy.sql.expression import update
from sqlalchemy.sql.functions import concat

from .exceptions import DuplicateError, ForeignKeyError, NotFoundError, InvalidArgumentsError
from .. import models
from ...api import schemas


class Logs:
    def __init__(self, session: AsyncSession):
        self.session = session

    async def get(self, id: UUID) -> schemas.Log:
        log = (
            await self.session.execute(
                select(models.Log)
                .where(models.Log.id == id)
            )
        ).scalar()

        if not log:
            raise NotFoundError(f'Log {id} does not exist')

        return schemas.Log.from_orm(log)

    async def get_body(self, id: UUID, offset: int | None = None, limit: int | None = None) -> str:
        args = [offset or 0]
        if limit:
            args.append(limit)

        body = (
            await self.session.execute(
                select(
                    func.substring(models.Log.body, *args)
                )
                .where(models.Log.id == id)
            )
        ).scalar()

        if not body:
            raise NotFoundError(f'Log {id} does not exist')

        return body

    async def get_all(self, test_run_id: UUID | None = None, test_id: UUID | None = None) -> [schemas.Log]:
        if not test_run_id and not test_id:
            raise InvalidArgumentsError('Test Run and/or Test id have to be provided')

        query = select(models.Log)

        if test_run_id:
            query = query.where(models.Log.test_run_id == test_run_id)

        if test_id:
            query = query.where(models.Log.test_id == test_id)

        logs = (await self.session.execute(query)).scalars().all()

        return [schemas.Log.from_orm(log) for log in logs]

    async def create(self, log: schemas.LogCreate) -> UUID:
        log.id = log.id or uuid4()
        log.start = log.start or datetime.datetime.utcnow()
        log = models.Log(**log.dict())
        self.session.add(log)

        try:
            await self.session.commit()
        except IntegrityError as e:
            if 'foreign key constraint' in e.orig.args[0]:
                raise ForeignKeyError(f'Test Run {log.test_run_id} or Test {log.test_id} does not exist')
            else:
                raise DuplicateError(f'Log {log.id} already exists')

        return log.id

    async def update(self, log: schemas.Log, exclude_unset: bool = False) -> UUID:
        try:
            result = (
                await self.session.execute(
                    update(models.Log)
                    .where(models.Log.id == log.id)
                    .values(**log.dict(exclude_unset=exclude_unset))
                )
            )
        except IntegrityError:
            raise NotFoundError(f'Test Run {log.test_run_id} or Test {log.test_id} does not exist')

        if result.rowcount < 1:
            raise NotFoundError(f'Log {log.id} does not exist')

        await self.session.commit()

        return log.id

    async def append_body(self, id: UUID, body: str) -> id:
        result = await self.session.execute(
            update(models.Log)
            .where(models.Log.id == id)
            .values(body=concat(models.Log.body, body))
        )

        if result.rowcount < 1:
            raise NotFoundError(f'Log {id} does not exist')

        await self.session.commit()

        return id
