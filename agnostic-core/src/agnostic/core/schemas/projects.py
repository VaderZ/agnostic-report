__all__ = ["Project", "ProjectUpdate", "ProjectCreate", "Projects"]
import uuid

from .base import Base, BaseRoot
from pydantic import Field


class ProjectUpdate(Base):
    name: str | None = None
    config: dict | None = None


class ProjectCreate(ProjectUpdate):
    name: str


class Project(ProjectCreate):
    id: uuid.UUID


class Projects(BaseRoot):
    root: list[Project]
