import datetime
from typing import List
from uuid import UUID, uuid4

from sqlalchemy.exc import IntegrityError
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy.future import select
from sqlalchemy.sql.expression import update

from agnostic.core import models, schemas
from .exceptions import DuplicateError, ForeignKeyError, NotFoundError


class Requests:
    def __init__(self, session: AsyncSession):
        self.session = session

    async def get(self, id: UUID) -> schemas.Request:
        metric = (
            await self.session.execute(
                select(models.Request)
                .where(models.Request.id == id)
            )
        ).scalar()

        if not metric:
            raise NotFoundError(f'Request {id} does not exist')

        return schemas.Request.model_validate(metric)

    async def get_all(self, test_id: UUID) -> List[schemas.Request]:
        requests = (await self.session.execute(
            select(models.Request)
            .where(models.Request.test_id == test_id)
        ))

        return [schemas.Request.model_validate(request) for request in requests]

    async def create(self, request: schemas.RequestCreate) -> UUID:
        request.id = request.id or uuid4()
        request.timestamp = request.timestamp or datetime.datetime.utcnow()
        request = models.Request(**request.model_dump())
        self.session.add(request)

        try:
            await self.session.commit()
        except IntegrityError as e:
            if 'foreign key constraint' in e.orig.args[0]:
                raise ForeignKeyError(f'Test Run {request.test_run_id} or Test {request.test_id} does not exist')
            else:
                raise DuplicateError(f'Request {request.id} already exists')

        return request.id

    async def update(self, request: schemas.Request, exclude_unset: bool = False) -> UUID:
        try:
            result = (
                await self.session.execute(
                    update(models.Request)
                    .where(models.Request.id == request.id)
                    .values(**request.model_dump(exclude_unset=exclude_unset))
                )
            )
        except IntegrityError:
            raise NotFoundError(f'Test Run {request.test_run_id} or Test {request.test_id} does not exist')

        if result.rowcount < 1:
            raise NotFoundError(f'Request {request.id} does not exist')

        await self.session.commit()

        return request.id
