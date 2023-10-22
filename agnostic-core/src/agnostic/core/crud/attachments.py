import uuid
from typing import Literal

from sqlalchemy.exc import IntegrityError
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy.sql.expression import select, and_, func

from agnostic.core import models as m
from agnostic.core.schemas import v2 as s
from .exceptions import DuplicateError, ForeignKeyError, NotFoundError


class Attachments:
    def __init__(self, session: AsyncSession):
        self.session = session

    def __get_columns(self, include: list[Literal["content"]] | None = None):
        columns = [
            m.Attachment.id,
            m.Attachment.test_run_id,
            m.Attachment.test_id,
            m.Attachment.timestamp,
            m.Attachment.name,
            m.Attachment.mime_type,
            m.Attachment.size,
        ]
        for column in include or []:
            columns.append(getattr(m.Attachment, column))
        return columns

    async def get(
        self, id_: uuid.UUID, include: list[Literal["content"]] | None = None
    ) -> s.Attachment:
        attachment = (
            await self.session.execute(
                select(*self.__get_columns(include)).where(m.Attachment.id == id_)
            )
        ).first()

        if not attachment:
            raise NotFoundError(f"Attachment {id_} does not exist")

        return s.Attachment.model_validate(attachment)

    async def get_all(
        self,
        test_run_id: uuid.UUID | None,
        test_id: uuid.UUID | None,
        page: int = 1,
        page_size: int = 100,
        include: list[Literal["content"]] | None = None,
    ) -> s.CRUDCollection:
        where = []
        if test_run_id:
            where.append(m.Attachment.test_run_id == test_run_id)
        if test_id:
            where.append(m.Attachment.test_id == test_id)
        count = (
            await self.session.execute(select(func.count(m.Attachment.id)).where(and_(*where)))
        ).scalar()
        attachments = (
            await self.session.execute(
                select(*self.__get_columns(include))
                .where(and_(*where))
                .order_by(m.Attachment.timestamp.desc())
                .offset(page_size * (page - 1))
                .limit(page_size)
            )
        ).all()

        return s.CRUDCollection(items=s.Attachments.model_validate(attachments), count=count)

    async def create(self, attachment: s.AttachmentCreate) -> uuid.UUID:
        attachment.id = attachment.id or uuid.uuid4()
        self.session.add(m.Attachment(**attachment.model_dump()))

        try:
            await self.session.commit()
        except IntegrityError as e:
            if "foreign key constraint" in e.orig.args[0]:
                raise ForeignKeyError(f"Test Run {attachment.test_run_id} does not exist")
            else:
                raise DuplicateError(f"Attachment {attachment.id} already exists")

        return attachment.id

    async def get_content(self, id_: uuid.UUID) -> bytes:
        content = (
            await self.session.execute(select(m.Attachment.content).where(m.Attachment.id == id_))
        ).scalar()

        if not content:
            raise NotFoundError(f"Attachment {id_} does not exist")

        return content
