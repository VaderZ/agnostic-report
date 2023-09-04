import datetime
import uuid
from decimal import Decimal

from sqlalchemy import Column, String, DateTime, Boolean, Text, ForeignKey, Integer, UniqueConstraint, CheckConstraint
from sqlalchemy.dialects.postgresql import UUID, DOUBLE_PRECISION, BYTEA, JSONB
from sqlalchemy.ext.declarative import as_declarative
from sqlalchemy.orm import mapped_column, Mapped
from sqlalchemy.sql import column, text


# Important note! While it looks logical to declare `test_id` columns as a foreign key on `tests.id`
# that's actually a terrible idea as it completely breaks scenario where test related items
# are reported from concurrent/parallel threads or processes


@as_declarative()
class Base:

    id: Mapped[uuid.UUID] = mapped_column(
        UUID(as_uuid=True),
        primary_key=True,
        default=uuid.uuid4,
        server_default=text('gen_random_uuid()'),
        unique=True,
        nullable=False
    )


class Project(Base):
    __tablename__ = 'projects'

    name: Mapped[str] = mapped_column(String(256), unique=True)
    config: Mapped[dict | None] = mapped_column(JSONB)


class TestRun(Base):
    __tablename__ = 'test_runs'

    project_id: Mapped[uuid.UUID] = mapped_column(
        UUID(as_uuid=True),
        ForeignKey('projects.id', ondelete='CASCADE'),
        nullable=False
    )
    start: Mapped[datetime.datetime] = mapped_column(DateTime, nullable=False)
    finish: Mapped[datetime.datetime | None] = mapped_column(DateTime)
    heartbeat: Mapped[datetime.datetime | None] = mapped_column(DateTime)
    keep_forever: Mapped[bool] = mapped_column(Boolean, default=False, server_default=text('false'))
    sut_version: Mapped[str | None] = mapped_column(String(128))
    sut_branch: Mapped[str | None] = mapped_column(String(128))
    test_version: Mapped[str | None] = mapped_column(String(128))
    test_branch: Mapped[str | None] = mapped_column(String(128))
    properties: Mapped[dict | None] = mapped_column(JSONB)


class TestRunVariant(Base):
    __tablename__ = 'test_run_variants'
    __table_args__ = (UniqueConstraint('test_run_id', 'name', name='unique_tr_variant'), )

    test_run_id: Mapped[uuid.UUID] = mapped_column(
        UUID(as_uuid=True),
        ForeignKey('test_runs.id', ondelete='CASCADE'),
        nullable=False
    )
    name: Mapped[str] = Column(String(128), nullable=False)
    value: Mapped[str] = Column(String(128), nullable=False)


class Test(Base):
    __tablename__ = 'tests'
    __table_args__ = (
        CheckConstraint(
            column('result').in_((None, 'passed', 'failed', 'skipped', 'xpassed', 'xfailed')),
            name='check_test_result'
        ),
    )

    test_run_id: Mapped[uuid.UUID] = mapped_column(
        UUID(as_uuid=True),
        ForeignKey('test_runs.id', ondelete='CASCADE'),
        nullable=False
    )
    start: Mapped[datetime.datetime] = mapped_column(DateTime, nullable=False)
    finish: Mapped[datetime.datetime | None] = mapped_column(DateTime)
    path: Mapped[str] = mapped_column(String(512), nullable=False)
    name: Mapped[str] = mapped_column(String(256), nullable=False)
    result: Mapped[str | None] = mapped_column(String(8))
    reason: Mapped[str | None] = mapped_column(Text)
    error_message: Mapped[str | None] = mapped_column(Text)
    description: Mapped[str | None] = mapped_column(Text)


class Log(Base):
    __tablename__ = 'logs'

    test_run_id: Mapped[uuid.UUID] = mapped_column(
        UUID(as_uuid=True),
        ForeignKey('test_runs.id', ondelete='CASCADE'),
        nullable=False
    )
    test_id: Mapped[uuid.UUID | None] = mapped_column(UUID(as_uuid=True))
    name: Mapped[str] = mapped_column(String(256), nullable=False)
    start: Mapped[datetime.datetime | None] = mapped_column(DateTime)
    finish: Mapped[datetime.datetime | None] = mapped_column(DateTime)
    body: Mapped[str] = mapped_column(Text)


class Metric(Base):
    __tablename__ = 'metrics'

    test_run_id: Mapped[uuid.UUID] = mapped_column(
        UUID(as_uuid=True),
        ForeignKey('test_runs.id', ondelete='CASCADE'),
        nullable=False
    )
    test_id: Mapped[uuid.UUID | None] = mapped_column(UUID(as_uuid=True))
    timestamp: Mapped[datetime.datetime] = mapped_column(DateTime, nullable=False)
    name: Mapped[str] = mapped_column(String(256), nullable=False)
    value: Mapped[Decimal] = mapped_column(DOUBLE_PRECISION, nullable=False)
    description: Mapped[str | None] = mapped_column(Text)


class Request(Base):
    __tablename__ = 'requests'

    test_run_id: Mapped[uuid.UUID] = mapped_column(
        UUID(as_uuid=True),
        ForeignKey('test_runs.id', ondelete='CASCADE'),
        nullable=False
    )
    test_id: Mapped[uuid.UUID | None] = mapped_column(UUID(as_uuid=True))
    request_type: Mapped[str] = mapped_column(String(128), nullable=False)
    timestamp: Mapped[datetime.datetime] = mapped_column(DateTime, nullable=False)
    contents: Mapped[dict] = mapped_column(JSONB, nullable=False)


class Progress(Base):
    __tablename__ = 'progress'

    test_run_id: Mapped[uuid.UUID] = mapped_column(
        UUID(as_uuid=True),
        ForeignKey('test_runs.id', ondelete='CASCADE'),
        nullable=False
    )
    test_id: Mapped[uuid.UUID | None] = mapped_column(UUID(as_uuid=True))
    timestamp: Mapped[datetime.datetime] = mapped_column(DateTime, nullable=False)
    level: Mapped[str] = mapped_column(String(10), nullable=False)
    message: Mapped[str] = mapped_column(Text, nullable=False)
    details: Mapped[str | None] = mapped_column(Text)


class Attachment(Base):
    __tablename__ = 'attachments'

    test_run_id: Mapped[uuid.UUID] = mapped_column(
        UUID(as_uuid=True),
        ForeignKey('test_runs.id', ondelete='CASCADE'),
        nullable=False
    )
    test_id: Mapped[uuid.UUID | None] = mapped_column(UUID(as_uuid=True))
    timestamp: Mapped[datetime.datetime] = mapped_column(DateTime, nullable=False)
    name: Mapped[str] = mapped_column(String(512), nullable=False)
    mime_type: Mapped[str] = mapped_column(String(128), nullable=False)
    size: Mapped[int] = mapped_column(Integer, nullable=False)
    content: Mapped[bytes] = mapped_column(BYTEA, nullable=False)


class MetricOverTime(Base):
    __tablename__ = 'metrics_over_time'

    test_run_id: Mapped[uuid.UUID] = mapped_column(
        UUID(as_uuid=True),
        ForeignKey('test_runs.id', ondelete='CASCADE'),
        nullable=False
    )
    test_id: Mapped[uuid.UUID | None] = mapped_column(UUID(as_uuid=True))
    name: Mapped[str] = mapped_column(String(128), nullable=False)
    timestamp: Mapped[datetime.datetime] = mapped_column(DateTime, nullable=False)
    values: Mapped[dict] = mapped_column(JSONB, nullable=False)
