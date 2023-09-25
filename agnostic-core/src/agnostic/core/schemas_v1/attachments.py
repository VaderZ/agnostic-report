__all__ = ['Attachment', 'AttachmentCreate']
import datetime
import uuid

from pydantic import constr

from .base import Base


class Attachment(Base):
    id: uuid.UUID
    test_run_id: uuid.UUID | None = None
    test_id: uuid.UUID | None = None
    timestamp: datetime.datetime | None = None
    name: constr(strip_whitespace=True, max_length=512)
    mime_type: constr(strip_whitespace=True, max_length=128)
    size: int | None = None
    content: bytes


class AttachmentCreate(Attachment):
    id: uuid.UUID | None = None
    name: constr(strip_whitespace=True, max_length=512)
    mime_type: constr(strip_whitespace=True, max_length=128)
    size: int | None = None
    content: bytes
