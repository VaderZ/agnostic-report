__all__ = ['Project', 'ProjectUpdate', 'ProjectCreate']
import uuid

from .base import Base


class ProjectUpdate(Base):
    id: uuid.UUID | None = None
    name: str | None = None
    config: dict | None = None


class ProjectCreate(ProjectUpdate):
    name: str


class Project(ProjectCreate):
    id: uuid.UUID
