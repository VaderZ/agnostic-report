import datetime
import uuid

from sqlalchemy.exc import IntegrityError
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy.sql.expression import select, update, and_, func

from agnostic.core import models as m
from agnostic.core.schemas import v2 as s
from .exceptions import DuplicateError, ForeignKeyError, NotFoundError


class Metrics:
    def __init__(self, session: AsyncSession):
        self.session = session

    async def get(self, id_: uuid.UUID) -> s.Metric:
        metric = (await self.session.execute(select(m.Metric).where(m.Metric.id == id_))).scalar()

        if not metric:
            raise NotFoundError(f"Metric {id_} does not exist")

        return s.Metric.model_validate(metric)

    async def get_all(
        self,
        test_run_id: uuid.UUID | None,
        test_id: uuid.UUID | None,
        page: int = 1,
        page_size: int = 100,
    ) -> s.CRUDCollection:
        where = []
        if test_run_id:
            where.append(m.Metric.test_run_id == test_run_id)
        if test_id:
            where.append(m.Metric.test_id == test_id)
        count = (
            await self.session.execute(select(func.count(m.Metric.id)).where(and_(*where)))
        ).scalar()
        metrics = (
            (
                await self.session.execute(
                    select(m.Metric)
                    .where(and_(*where))
                    .order_by(m.Metric.timestamp.desc())
                    .offset(page_size * (page - 1))
                    .limit(page_size)
                )
            )
            .scalars()
            .all()
        )

        return s.CRUDCollection(items=s.Metrics.model_validate(metrics), count=count)

    async def create(self, metric: s.MetricCreate) -> uuid.UUID:
        metric.id = metric.id or uuid.uuid4()
        metric.timestamp = metric.timestamp or datetime.datetime.now(datetime.UTC)
        self.session.add(m.Metric(**metric.model_dump()))

        try:
            await self.session.commit()
        except IntegrityError as e:
            if "foreign key constraint" in e.orig.args[0]:
                raise ForeignKeyError(f"Test Run {metric.test_run_id} does not exist")
            else:
                raise DuplicateError(f"Metric {metric.id} already exists")

        return metric.id

    async def update(
        self, id_: uuid.UUID, metric: s.MetricUpdate | s.MetricPatch, exclude_unset: bool = False
    ) -> uuid.UUID:
        try:
            result = await self.session.execute(
                update(m.Metric)
                .where(m.Metric.id == id_)
                .values(**metric.model_dump(exclude_unset=exclude_unset))
            )
        except IntegrityError:
            raise NotFoundError(f"Test Run {metric.test_run_id} does not exist")

        if result.rowcount < 1:
            raise NotFoundError(f"Metric {metric.id} does not exist")

        await self.session.commit()

        return id_
