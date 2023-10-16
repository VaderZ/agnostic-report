__all__ = ["ProgressPatch", "ProgressUpdate", "ProgressCreate", "Progress", "Progresses"]
import datetime
import uuid

from pydantic import Field

from .base import Base, BaseRoot
from .lookups import Level


class ProgressPatch(Base):
    timestamp: datetime.datetime | None = None
    level: Level | None = None
    message: str | None = None
    details: str | None = None


class ProgressUpdate(ProgressPatch):
    level: Level | None
    message: str | None


class ProgressCreate(ProgressUpdate):
    id: uuid.UUID | None = Field(default_factory=uuid.uuid4)
    test_run_id: uuid.UUID
    test_id: uuid.UUID | None = None


class Progress(ProgressCreate):
    id: uuid.UUID


class Progresses(BaseRoot):
    root: list[Progress]
