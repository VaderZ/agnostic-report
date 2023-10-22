__all__ = ["AttachmentCreate", "Attachment", "Attachments"]
import base64
import datetime
import uuid

from pydantic import constr, Field, field_validator

from .base import Base, BaseRoot


class AttachmentCreate(Base):
    id: uuid.UUID | None = Field(default_factory=uuid.uuid4)
    test_run_id: uuid.UUID
    test_id: uuid.UUID | None = None
    timestamp: datetime.datetime | None = None
    name: constr(strip_whitespace=True, max_length=512)
    mime_type: constr(strip_whitespace=True, max_length=128)
    size: int | None = None
    content: bytes


class Attachment(AttachmentCreate):
    id: uuid.UUID
    content: str | None = ""

    @field_validator("content", mode="before")
    def content_to_b64(cls, value):
        if isinstance(value, bytes):
            return base64.b64encode(value)
        return value


class Attachments(BaseRoot):
    root: list[Attachment]
