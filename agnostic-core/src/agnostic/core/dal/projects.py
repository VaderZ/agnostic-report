from uuid import UUID, uuid4

from sqlalchemy.exc import IntegrityError
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy.future import select
from sqlalchemy.sql.expression import update

from agnostic.core import models, schemas
from .exceptions import DuplicateError, NotFoundError


class Projects:
    def __init__(self, session: AsyncSession):
        self.session = session

    async def get(self, id: UUID) -> schemas.Project | None:
        project = (
            await self.session.execute(
                select(models.Project)
                .where(models.Project.id == id)
            )
        ).scalar()

        if not project:
            raise NotFoundError(f'Project {id} does not exist')

        return schemas.Project.model_validate(project)

    async def get_all(self) -> list[schemas.Project]:
        projects = (
            await self.session.execute(
                select(models.Project)
            )
        ).scalars().all()
        return [schemas.Project.model_validate(project) for project in projects]

    async def create(self, project: schemas.ProjectCreate | schemas.Project) -> UUID:
        project = models.Project(**project.model_dump())
        self.session.add(project)

        try:
            await self.session.commit()
        except IntegrityError:
            raise DuplicateError(f'Project "{project.name}" already exists')

        return project.id

    async def update(self, project: schemas.Project, exclude_unset: bool = False) -> UUID:
        try:
            result = await self.session.execute(
                update(models.Project)
                .where(models.Project.id == project.id)
                .values(**project.model_dump(exclude_unset=exclude_unset))
            )
            await self.session.commit()
        except IntegrityError:
            raise DuplicateError(f'Project "{project.name}" already exists')

        if result.rowcount < 1:
            raise NotFoundError(f'Project {project.id} does not exist')

        return project.id
