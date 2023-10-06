import uuid

from sqlalchemy import select, update, func
from sqlalchemy.exc import IntegrityError
from sqlalchemy.ext.asyncio import AsyncSession

from agnostic.core import models as m
from agnostic.core.schemas import v2 as s
from .exceptions import DuplicateError, NotFoundError


class Projects:
    def __init__(self, session: AsyncSession):
        self.session = session

    async def get(self, id_: uuid.UUID) -> s.Project:
        project = (
            await self.session.execute(select(m.Project).where(m.Project.id == id_))
        ).scalar()

        if not project:
            raise NotFoundError(f"Project {id} does not exist")

        return s.Project.model_validate(project)

    async def get_all(self, page: int = 1, page_size: int = 100) -> s.CRUDCollection:
        count = (await self.session.execute(select(func.count(m.Project.id)))).scalar()
        projects = (
            (
                await self.session.execute(
                    select(m.Project)
                    .order_by(m.Project.id)
                    .offset(page_size * (page - 1))
                    .limit(page_size)
                )
            )
            .scalars()
            .all()
        )
        return s.CRUDCollection(count=count, items=s.Projects.model_validate(projects))

    async def create(self, project: s.ProjectCreate | s.ProjectUpdate) -> uuid.UUID:
        project = m.Project(**project.model_dump())
        self.session.add(project)

        try:
            await self.session.commit()
        except IntegrityError:
            raise DuplicateError(f'Project {project.id} or "{project.name}" already exists')

        return project.id

    async def update(
        self, id_: uuid.UUID, project: s.ProjectUpdate | s.ProjectPatch, exclude_unset: bool = False
    ) -> uuid.UUID:
        try:
            result = await self.session.execute(
                update(m.Project)
                .where(m.Project.id == id_)
                .values(**project.model_dump(exclude_unset=exclude_unset))
            )
            await self.session.commit()
        except IntegrityError:
            raise DuplicateError(f'Project {project.id}, "{project.name}" already exists')

        if result.rowcount < 1:
            raise NotFoundError(f"Project {project.id} does not exist")

        return id_
