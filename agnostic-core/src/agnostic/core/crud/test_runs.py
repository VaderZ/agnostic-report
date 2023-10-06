import datetime
import uuid

from sqlalchemy.exc import IntegrityError
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy.sql.expression import select, update, delete, and_, func

from agnostic.core import models as m
from agnostic.core.schemas import v2 as s
from .exceptions import DuplicateError, ForeignKeyError, NotFoundError


class TestRuns:
    def __init__(self, session: AsyncSession):
        self.session = session
        self.__get_query = select(
            m.TestRun.id,
            m.TestRun.project_id,
            m.TestRun.start,
            m.TestRun.finish,
            m.TestRun.heartbeat,
            m.TestRun.keep_forever,
            m.TestRun.sut_branch,
            m.TestRun.sut_version,
            m.TestRun.test_version,
            m.TestRun.properties,
            func.jsonb_agg(m.TestRunVariant.__table__.table_valued())
            .filter(m.TestRunVariant.name.isnot(None))
            .label("variant"),
        ).outerjoin(m.TestRunVariant, m.TestRun.id == m.TestRunVariant.test_run_id)

    async def get(self, id_: uuid.UUID) -> s.TestRun:
        test_run = (
            await self.session.execute(
                self.__get_query.where(m.TestRun.id == id_).group_by(m.TestRun.id)
            )
        ).one()

        if not test_run:
            raise NotFoundError(f"Test Run {id_} does not exist")

        return s.TestRun.model_validate(test_run)

    async def get_all(
        self, project_id: uuid.UUID | None, page: int = 1, page_size: int = 100
    ) -> s.CRUDCollection:
        where = []
        if project_id:
            where.append(m.TestRun.project_id == project_id)
        count = (
            await self.session.execute(select(func.count(m.TestRun.id)).where(and_(*where)))
        ).scalar()
        test_runs = (
            await self.session.execute(
                self.__get_query.where(and_(*where))
                .group_by(m.TestRun.id)
                .order_by(m.TestRun.start.desc())
                .offset(page_size * (page - 1))
                .limit(page_size)
            )
        ).all()

        return s.CRUDCollection(items=s.TestRuns.model_validate(test_runs), count=count)

    async def create(self, test_run: s.TestRunCreate) -> uuid.UUID:
        test_run.id = test_run.id or uuid.uuid4()
        test_run.start = test_run.start or datetime.datetime.utcnow()
        test_run.heartbeat = test_run.heartbeat or datetime.datetime.utcnow()
        self.session.add(m.TestRun(**test_run.model_dump(exclude={"variant"})))

        for variant in test_run.variant or []:
            self.session.add(
                m.TestRunVariant(test_run_id=test_run.id, name=variant.name, value=variant.value)
            )

        try:
            await self.session.commit()
        except IntegrityError as e:
            if "foreign key constraint" in e.orig.args[0]:
                raise ForeignKeyError(f"Project {test_run.project_id} does not exist")
            else:
                raise DuplicateError(f"Test Run {test_run.id} already exists")

        return test_run.id

    async def update(
        self,
        id_: uuid.UUID,
        test_run: s.TestRunUpdate | s.TestRunPatch,
        exclude_unset: bool = False,
    ) -> uuid.UUID:
        try:
            fields = test_run.model_dump(exclude={"variant"}, exclude_unset=exclude_unset)
            if len(fields):
                # In case patch has only variant fields will be empty
                result = await self.session.execute(
                    update(m.TestRun).where(m.TestRun.id == id_).values(**fields)
                )

                if result.rowcount < 1:
                    raise NotFoundError(f"Test Run {id_} does not exist")

        except IntegrityError:
            raise NotFoundError(f"Project {id_} does not exist")

        if not exclude_unset or (exclude_unset and test_run.variant is not None):
            await self.session.execute(
                delete(m.TestRunVariant).where(m.TestRunVariant.test_run_id == id_)
            )

        for variant in test_run.variant or []:
            self.session.add(
                m.TestRunVariant(test_run_id=id_, name=variant.name, value=variant.value)
            )

        await self.session.commit()

        return id_
