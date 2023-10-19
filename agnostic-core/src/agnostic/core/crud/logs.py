import datetime
import uuid
from typing import Literal

from sqlalchemy.exc import IntegrityError
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy.sql.expression import select, update, and_, func

from agnostic.core import models as m
from agnostic.core.schemas import v2 as s
from .exceptions import DuplicateError, ForeignKeyError, NotFoundError


class Logs:
    def __init__(self, session: AsyncSession):
        self.session = session

    def __get_columns(self, include: list[Literal["body"]] | None = None):
        columns = [
            m.Log.id,
            m.Log.test_run_id,
            m.Log.test_id,
            m.Log.name,
            m.Log.start,
            m.Log.finish,
        ]
        for column in include or []:
            columns.append(getattr(m.Log, column))
        return columns

    async def get(self, id_: uuid.UUID, include: list[Literal["body"]] | None = None) -> s.Log:
        log = (
            await self.session.execute(select(*self.__get_columns(include)).where(m.Log.id == id_))
        ).first()

        if not log:
            raise NotFoundError(f"Log {id_} does not exist")

        return s.Log.model_validate(log)

    async def get_all(
        self,
        test_run_id: uuid.UUID | None,
        test_id: uuid.UUID | None,
        page: int = 1,
        page_size: int = 100,
        include: list[Literal["body"]] | None = None,
    ) -> s.CRUDCollection:
        where = []
        if test_run_id:
            where.append(m.Log.test_run_id == test_run_id)
        if test_id:
            where.append(m.Log.test_id == test_id)
        count = (
            await self.session.execute(select(func.count(m.Log.id)).where(and_(*where)))
        ).scalar()
        logs = (
            await self.session.execute(
                select(*self.__get_columns(include))
                .where(and_(*where))
                .order_by(m.Log.start.desc())
                .offset(page_size * (page - 1))
                .limit(page_size)
            )
        ).all()

        return s.CRUDCollection(items=s.Logs.model_validate(logs), count=count)

    async def create(self, log: s.LogCreate) -> uuid.UUID:
        log.id = log.id or uuid.uuid4()
        log.start = log.start or datetime.datetime.now(datetime.UTC)
        self.session.add(m.Log(**log.model_dump()))

        try:
            await self.session.commit()
        except IntegrityError as e:
            if "foreign key constraint" in e.orig.args[0]:
                raise ForeignKeyError(f"Test Run {log.test_run_id} does not exist")
            else:
                raise DuplicateError(f"Log {log.id} already exists")

        return log.id

    async def update(
        self, id_: uuid.UUID, log: s.LogUpdate | s.LogPatch, exclude_unset: bool = False
    ) -> uuid.UUID:
        try:
            result = await self.session.execute(
                update(m.Log)
                .where(m.Log.id == id_)
                .values(**log.model_dump(exclude_unset=exclude_unset))
            )
        except IntegrityError:
            raise NotFoundError(f"Test Run {log.test_run_id} does not exist")

        if result.rowcount < 1:
            raise NotFoundError(f"Log {log.id} does not exist")

        await self.session.commit()

        return id_

    async def get_body(self, id_: uuid.UUID) -> str:
        body = (await self.session.execute(select(m.Log.body).where(m.Log.id == id_))).scalar()

        if not body:
            raise NotFoundError(f"Log {id_} does not exist")

        return body

    async def append_body(self, id_: uuid.UUID, body: str) -> uuid.UUID:
        result = await self.session.execute(
            update(m.Log).where(m.Log.id == id_).values(body=func.concat(m.Log.body, body))
        )

        if result.rowcount < 1:
            raise NotFoundError(f"Log {id} does not exist")

        await self.session.commit()

        return id_
