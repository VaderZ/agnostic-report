import datetime
from uuid import UUID, uuid4

from sqlalchemy.exc import IntegrityError
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy.future import select
from sqlalchemy.sql.expression import update

from agnostic.core import models, schemas
from .exceptions import DuplicateError, ForeignKeyError, NotFoundError


class Tests:
    def __init__(self, session: AsyncSession):
        self.session = session

    async def get(self, id: UUID) -> schemas.v1.Test:
        test = (
            await self.session.execute(
                select(models.Test)
                .where(models.Test.id == id)
            )
        ).scalar()

        if not test:
            raise NotFoundError(f'Test {id} does not exist')

        return schemas.v1.Test.model_validate(test)

    async def get_all(self, test_run_id: UUID) -> [schemas.v1.TestRun]:
        tests = (
            await self.session.execute(
                select(models.Test)
                .where(models.Test.test_run_id == test_run_id)
            )).scalars().all()

        return [schemas.v1.Test.model_validate(test) for test in tests]

    async def create(self, test: schemas.v1.Test) -> UUID:
        test.id = test.id or uuid4()
        test.start = test.start or datetime.datetime.utcnow()
        test = models.Test(**test.model_dump())
        self.session.add(test)

        try:
            await self.session.commit()
        except IntegrityError as e:
            if 'foreign key constraint' in e.orig.args[0]:
                raise ForeignKeyError(f'Test Run {test.test_run_id} does not exist')
            else:
                raise DuplicateError(f'Test {test.id} already exists')

        return test.id

    async def update(self, test: schemas.v1.Test, exclude_unset: bool = False) -> UUID:
        try:
            result = (
                await self.session.execute(
                    update(models.Test)
                    .where(models.Test.id == test.id)
                    .values(**test.model_dump(exclude_unset=exclude_unset))
                )
            )
        except IntegrityError:
            raise NotFoundError(f'Test Run {test.test_run_id} does not exist')

        if result.rowcount < 1:
            raise NotFoundError(f'Test {test.id} does not exist')

        await self.session.commit()

        return test.id
