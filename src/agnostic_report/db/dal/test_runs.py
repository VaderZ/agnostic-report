import copy
import datetime
from uuid import UUID, uuid4

from sqlalchemy.dialects.postgresql import insert
from sqlalchemy.exc import IntegrityError
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy.future import select
from sqlalchemy.sql.expression import update, delete

from .exceptions import DuplicateError, ForeignKeyError, NotFoundError
from .. import models
from ...api import schemas


class TestRuns:
    def __init__(self, session: AsyncSession):
        self.session = session

    async def __update_variant(self, id: UUID, variant: dict):
        variants = (await self.session.execute(
            select(models.TestRunVariant)
            .where(models.TestRunVariant.test_run_id == id)
        )).scalars().all()

        _variant = copy.copy(variant)
        values = []

        for var in variants:
            if var.name and var.name not in variant:
                await self.session.execute(
                    delete(models.TestRunVariant)
                    .where(models.TestRunVariant.test_run_id == id,
                           models.TestRunVariant.name == var.name)
                )
            else:
                values.append({'id': var.id, 'test_run_id': id,
                               'name': var.name, 'value': variant[var.name]})
                del _variant[var.name]

        for key, val in _variant.items():
            values.append({'id': uuid4(), 'test_run_id': id,
                           'name': key, 'value': val})

        statement = insert(models.TestRunVariant).values(values)
        statement = statement.on_conflict_do_update(
            constraint='unique_tr_variant',
            set_={'value': statement.excluded.value}
        )

        await self.session.execute(statement)

    async def __get_variant(self, id: UUID | list[UUID]) -> dict[UUID, dict]:
        # TODO: Find a way to do that in SQL
        #  as this approach is ineffective
        ids = id
        if isinstance(ids, UUID):
            ids = [id]
        variants = (await self.session.execute(
            select(models.TestRunVariant)
            .where(models.TestRunVariant.test_run_id.in_(ids))
        )).scalars().all()

        result = {}
        for variant in variants:
            if variant.test_run_id not in result:
                result[variant.test_run_id] = {}
            result[variant.test_run_id].update({variant.name: variant.value})

        return result

    async def get(self, id: UUID) -> schemas.TestRun:
        test_run = (
            await self.session.execute(
                select(models.TestRun)
                .where(models.TestRun.id == id)
            )
        ).scalar()

        if not test_run:
            raise NotFoundError(f'Test Run {id} does not exist')

        test_run = schemas.TestRun.from_orm(test_run)
        try:
            test_run.variant = (await self.__get_variant(id))[id]
        except KeyError:
            test_run.variant = {}
        return test_run

    async def get_all(self, project_id: UUID) -> [schemas.TestRun]:
        test_runs = (
            await self.session.execute(
                select(models.TestRun)
                .where(models.TestRun.project_id == project_id)
            )).scalars().all()

        result = []
        variants = await self.__get_variant([test_run.id for test_run in test_runs])
        for test_run in test_runs:
            test_run.variant = variants[test_run.id]
            result.append(test_run)

        return result

    async def create(self, test_run: schemas.TestRun) -> UUID:
        test_run.id = test_run.id or uuid4()
        test_run.start = test_run.start or datetime.datetime.utcnow()
        test_run.heartbeat = test_run.heartbeat or datetime.datetime.utcnow()
        variant = test_run.variant
        test_run = models.TestRun(**test_run.dict(exclude={'variant'}))
        self.session.add(test_run)

        if variant is not None:
            await self.__update_variant(test_run.id, variant)

        try:
            await self.session.commit()
        except IntegrityError as e:
            if 'foreign key constraint' in e.orig.args[0]:
                raise ForeignKeyError(f'Project {test_run.project_id} does not exist')
            else:
                raise DuplicateError(f'Test Run {test_run.id} already exists')

        return test_run.id

    async def update(self, test_run: schemas.TestRun, exclude_unset: bool = False) -> UUID:
        try:
            result = (
                await self.session.execute(
                    update(models.TestRun)
                    .where(models.TestRun.id == test_run.id)
                    .values(**test_run.dict(exclude={'variant'}, exclude_unset=exclude_unset))
                )
            )
        except IntegrityError:
            raise NotFoundError(f'Project {test_run.id} does not exist')

        if result.rowcount < 1:
            raise NotFoundError(f'Test Run {test_run.id} does not exist')

        if test_run.variant is not None:
            await self.__update_variant(test_run.id, test_run.variant)

        await self.session.commit()

        return test_run.id
