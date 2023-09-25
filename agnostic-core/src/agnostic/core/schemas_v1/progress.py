__all__ = ['Progress', 'ProgressCreate']
import uuid
import datetime
from .base import Base
from .lookups import Level


class Progress(Base):
    id: uuid.UUID
    test_run_id: uuid.UUID | None = None
    test_id: uuid.UUID | None = None
    timestamp: datetime.datetime | None = None
    level: Level | None = None
    message: str | None = None
    details: str | None = None


class ProgressCreate(Progress):
    id: uuid.UUID | None = None
    message: str
    level: Level
    