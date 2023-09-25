import datetime
from uuid import UUID, uuid4

from sqlalchemy.exc import IntegrityError
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy.future import select
from sqlalchemy.sql.expression import update

from agnostic.core import models, schemas
from .exceptions import DuplicateError, ForeignKeyError, NotFoundError, InvalidArgumentsError


class Attachments:
    def __init__(self, session: AsyncSession):
        self.session = session

    async def get(self, id: UUID) -> schemas.v1.Attachment:
        attachment = (
            await self.session.execute(
                select(models.Attachment)
                .where(models.Attachment.id == id)
            )
        ).scalar()

        if not attachment:
            raise NotFoundError(f'Attachment {id} does not exist')

        return schemas.v1.Attachment.model_validate(attachment)

    async def get_all(self, test_run_id: UUID | None = None, test_id: UUID | None = None) -> [schemas.v1.Attachment]:
        if not test_run_id and not test_id:
            raise InvalidArgumentsError('Test Run and/or Test id have to be provided')

        query = select(models.Attachment)

        if test_run_id:
            query = query.where(models.Attachment.test_run_id == test_run_id)

        if test_id:
            query = query.where(models.Attachment.test_id == test_id)

        attachments = (await self.session.execute(query)).scalars().all()

        return [schemas.v1.Attachment.model_validate(attachment) for attachment in attachments]

    async def create(self, attachment: schemas.v1.AttachmentCreate) -> UUID:
        attachment.id = attachment.id or uuid4()
        attachment.timestamp = attachment.timestamp or datetime.datetime.utcnow()
        attachment = models.Attachment(**attachment.model_dump())
        self.session.add(attachment)

        try:
            await self.session.commit()
        except IntegrityError as e:
            if 'foreign key constraint' in e.orig.args[0]:
                raise ForeignKeyError(f'Test Run {attachment.test_run_id} or Test {attachment.test_id} does not exist')
            else:
                raise DuplicateError(f'Attachment {attachment.id} already exists')

        return attachment.id

    async def update(self, attachment: schemas.v1.Attachment, exclude_unset: bool = False) -> UUID:
        try:
            result = (
                await self.session.execute(
                    update(models.Attachment)
                    .where(models.Attachment.id == attachment.id)
                    .values(**attachment.model_dump(exclude_unset=exclude_unset))
                )
            )
        except IntegrityError:
            raise NotFoundError(f'Test Run {attachment.test_run_id} or Test {attachment.test_id} does not exist')

        if result.rowcount < 1:
            raise NotFoundError(f'Attachment {attachment.id} does not exist')

        await self.session.commit()

        return attachment.id
