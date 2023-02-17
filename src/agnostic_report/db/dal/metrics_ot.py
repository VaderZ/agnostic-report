import datetime
from uuid import UUID, uuid4

from sqlalchemy.exc import IntegrityError
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy.future import select
from sqlalchemy.sql.expression import update

from .exceptions import DuplicateError, ForeignKeyError, NotFoundError, InvalidArgumentsError
from .. import models
from ...api import schemas


class MetricsOverTime:
    def __init__(self, session: AsyncSession):
        self.session = session

    async def get(self, id: UUID) -> schemas.MetricOverTime:
        metric = (
            await self.session.execute(
                select(models.MetricOverTime)
                .where(models.MetricOverTime.id == id)
            )
        ).scalar()

        if not metric:
            raise NotFoundError(f'Metric {id} does not exist')

        return schemas.MetricOverTime.from_orm(metric)

    async def get_all(self, test_run_id: UUID | None = None, test_id: UUID | None = None) -> [schemas.MetricOverTime]:
        if not test_run_id and not test_id:
            raise InvalidArgumentsError('Test Run and/or Test id have to be provided')

        query = select(models.MetricOverTime)

        if test_run_id:
            query = query.where(models.MetricOverTime.test_run_id == test_run_id)

        if test_id:
            query = query.where(models.MetricOverTime.test_id == test_id)

        metrics = (await self.session.execute(query)).scalars().all()

        return [schemas.MetricOverTime.from_orm(metric) for metric in metrics]

    async def create(self, metric: schemas.MetricOverTime) -> UUID:
        metric.id = metric.id or uuid4()
        metric.timestamp = metric.timestamp or datetime.datetime.utcnow()
        metric = models.MetricOverTime(**metric.dict())
        self.session.add(metric)

        try:
            await self.session.commit()
        except IntegrityError as e:
            if 'foreign key constraint' in e.orig.args[0]:
                raise ForeignKeyError(f'Test Run {metric.test_run_id} or Test {metric.test_id} does not exist')
            else:
                raise DuplicateError(f'Metric {metric.id} already exists')

        return metric.id

    async def update(self, metric: schemas.MetricOverTime, exclude_unset: bool = False) -> UUID:
        try:
            result = (
                await self.session.execute(
                    update(models.MetricOverTime)
                    .where(models.MetricOverTime.id == metric.id)
                    .values(**metric.dict(exclude_unset=exclude_unset))
                )
            )
        except IntegrityError:
            raise NotFoundError(f'Test Run {metric.test_run_id} or Test {metric.test_id} does not exist')

        if result.rowcount < 1:
            raise NotFoundError(f'Metric {metric.id} does not exist')

        await self.session.commit()

        return metric.id
