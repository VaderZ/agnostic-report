__all__ = ["Project", "ProjectPatch", "ProjectUpdate", "ProjectCreate", "Projects"]
import uuid

from pydantic import Field

from .base import Base, BaseRoot


class ProjectPatch(Base):
    name: str | None = None
    config: dict | None = None


class ProjectUpdate(Base):
    name: str
    config: dict | None = None


class ProjectCreate(ProjectUpdate):
    id: uuid.UUID | None = Field(default_factory=uuid.uuid4)


class Project(ProjectCreate):
    id: uuid.UUID


class Projects(BaseRoot):
    root: list[Project]
