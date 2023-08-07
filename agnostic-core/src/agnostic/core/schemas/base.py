__all__ = ['Base']
from uuid import UUID

from pydantic import BaseModel


class Base(BaseModel):
    id: UUID | None

    class Config:
        orm_mode = True
