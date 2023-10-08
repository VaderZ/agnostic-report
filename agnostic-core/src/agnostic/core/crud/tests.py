import datetime
import uuid

from sqlalchemy.exc import IntegrityError
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy.sql.expression import select, update, and_, func

from agnostic.core import models as m
from agnostic.core.schemas import v2 as s
from .exceptions import DuplicateError, ForeignKeyError, NotFoundError


class Tests:
    def __init__(self, session: AsyncSession):
        self.session = session

    async def get(self, id_: uuid.UUID) -> s.Test:
        test = (await self.session.execute(select(m.Test).where(m.Test.id == id_))).scalar()

        if not test:
            raise NotFoundError(f"Test {id_} does not exist")

        return s.Test.model_validate(test)

    async def get_all(
        self, test_run_id: uuid.UUID | None, page: int = 1, page_size: int = 100
    ) -> s.CRUDCollection:
        where = []
        if test_run_id:
            where.append(m.Test.test_run_id == test_run_id)
        count = (
            await self.session.execute(select(func.count(m.Test.id)).where(and_(*where)))
        ).scalar()
        tests = (
            (
                await self.session.execute(
                    select(m.Test)
                    .where(and_(*where))
                    .order_by(m.Test.start.desc())
                    .offset(page_size * (page - 1))
                    .limit(page_size)
                )
            )
            .scalars()
            .all()
        )

        return s.CRUDCollection(items=s.Tests.model_validate(tests), count=count)

    async def create(self, test: s.TestCreate) -> uuid.UUID:
        test.id = test.id or uuid.uuid4()
        test.start = test.start or datetime.datetime.now(datetime.UTC)
        self.session.add(m.Test(**test.model_dump()))

        try:
            await self.session.commit()
        except IntegrityError as e:
            if "foreign key constraint" in e.orig.args[0]:
                raise ForeignKeyError(f"Test Run {test.test_run_id} does not exist")
            else:
                raise DuplicateError(f"Test {test.id} already exists")

        return test.id

    async def update(
        self, id_: uuid.UUID, test: s.TestUpdate | s.TestPatch, exclude_unset: bool = False
    ) -> uuid.UUID:
        try:
            result = await self.session.execute(
                update(m.Test)
                .where(m.Test.id == id_)
                .values(**test.model_dump(exclude_unset=exclude_unset))
            )
        except IntegrityError:
            raise NotFoundError(f"Test Run {test.test_run_id} does not exist")

        if result.rowcount < 1:
            raise NotFoundError(f"Test {test.id} does not exist")

        await self.session.commit()

        return id_
