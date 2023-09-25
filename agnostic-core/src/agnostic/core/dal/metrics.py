import datetime
from uuid import UUID, uuid4

from sqlalchemy.exc import IntegrityError
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy.future import select
from sqlalchemy.sql.expression import update

from agnostic.core import models, schemas
from .exceptions import DuplicateError, ForeignKeyError, NotFoundError, InvalidArgumentsError


class Metrics:
    def __init__(self, session: AsyncSession):
        self.session = session

    async def get(self, id: UUID) -> schemas.v1.Metric:
        metric = (
            await self.session.execute(
                select(models.Metric)
                .where(models.Metric.id == id)
            )
        ).scalar()

        if not metric:
            raise NotFoundError(f'Metric {id} does not exist')

        return schemas.v1.Metric.model_validate(metric)

    async def get_all(self, test_run_id: UUID | None = None, test_id: UUID | None = None) -> [schemas.v1.Metric]:
        if not test_run_id and not test_id:
            raise InvalidArgumentsError('Test Run and/or Test id have to be provided')

        query = select(models.Metric)

        if test_run_id:
            query = query.where(models.Metric.test_run_id == test_run_id)

        if test_id:
            query = query.where(models.Metric.test_id == test_id)

        metrics = (await self.session.execute(query)).scalars().all()

        return [schemas.v1.Metric.model_validate(metric) for metric in metrics]

    async def create(self, metric: schemas.v1.MetricCreate) -> UUID:
        metric.id = metric.id or uuid4()
        metric.timestamp = metric.timestamp or datetime.datetime.utcnow()
        metric = models.Metric(**metric.model_dump())
        self.session.add(metric)

        try:
            await self.session.commit()
        except IntegrityError as e:
            if 'foreign key constraint' in e.orig.args[0]:
                raise ForeignKeyError(f'Test Run {metric.test_run_id} or Test {metric.test_id} does not exist')
            else:
                raise DuplicateError(f'Metric {metric.id} already exists')

        return metric.id

    async def update(self, metric: schemas.v1.Metric, exclude_unset: bool = False) -> UUID:
        try:
            result = (
                await self.session.execute(
                    update(models.Metric)
                    .where(models.Metric.id == metric.id)
                    .values(**metric.model_dump(exclude_unset=exclude_unset))
                )
            )
        except IntegrityError:
            raise NotFoundError(f'Test Run {metric.test_run_id} or Test {metric.test_id} does not exist')

        if result.rowcount < 1:
            raise NotFoundError(f'Metric {metric.id} does not exist')

        await self.session.commit()

        return metric.id
