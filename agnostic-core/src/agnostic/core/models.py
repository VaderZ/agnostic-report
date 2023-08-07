import uuid

from sqlalchemy import Column, String, DateTime, Boolean, Text, ForeignKey, Integer, UniqueConstraint, CheckConstraint
from sqlalchemy.dialects.postgresql import UUID, DOUBLE_PRECISION, BYTEA, JSONB
from sqlalchemy.ext.declarative import as_declarative
from sqlalchemy.orm import relationship, backref
from sqlalchemy.sql import column


@as_declarative()
class Base:

    id = Column(UUID(as_uuid=True), primary_key=True, default=uuid.uuid4, unique=True, nullable=False)


class Project(Base):
    __tablename__ = 'projects'

    name = Column(String(256), unique=True)
    config = Column(JSONB)


class TestRun(Base):
    __tablename__ = 'test_runs'

    project_id = Column(UUID(as_uuid=True), ForeignKey('projects.id', ondelete='CASCADE'))
    start = Column(DateTime)
    finish = Column(DateTime)
    heartbeat = Column(DateTime)
    keep_forever = Column(Boolean, default=False)
    sut_version = Column(String(128))
    sut_branch = Column(String(128))
    test_version = Column(String(128))
    test_branch = Column(String(128))
    properties = Column(JSONB)

    test_run = relationship('Project', backref=backref('test_runs', passive_deletes=True))


class TestRunVariant(Base):
    __tablename__ = 'test_run_variants'
    __table_args__ = (UniqueConstraint('test_run_id', 'name', name='unique_tr_variant'), )

    test_run_id = Column(UUID(as_uuid=True), ForeignKey('test_runs.id', ondelete='CASCADE'))
    name = Column(String(128))
    value = Column(String(128))

    test_run = relationship('TestRun', backref=backref('variants', passive_deletes=True))


class Test(Base):
    __tablename__ = 'tests'
    __table_args__ = (
        CheckConstraint(
            column('result').in_((None, 'passed', 'failed', 'skipped', 'xpassed', 'xfailed')),
            name='check_test_result'
        ),
    )

    test_run_id = Column(UUID(as_uuid=True), ForeignKey('test_runs.id', ondelete='CASCADE'))
    start = Column(DateTime)
    finish = Column(DateTime)
    path = Column(String(512))
    name = Column(String(256))
    result = Column(String(8))
    reason = Column(Text)
    error_message = Column(Text)
    description = Column(Text)

    test_run = relationship('TestRun', backref=backref('tests', passive_deletes=True))


class Log(Base):
    __tablename__ = 'logs'

    test_run_id = Column(UUID(as_uuid=True), ForeignKey('test_runs.id', ondelete='CASCADE'))
    test_id = Column(UUID(as_uuid=True))
    name = Column(String(256))
    start = Column(DateTime)
    finish = Column(DateTime)
    body = Column(Text)

    test_run = relationship('TestRun', backref=backref('logs', passive_deletes=True))


class Metric(Base):
    __tablename__ = 'metrics'

    test_run_id = Column(UUID(as_uuid=True), ForeignKey('test_runs.id', ondelete='CASCADE'))
    test_id = Column(UUID(as_uuid=True))
    timestamp = Column(DateTime)
    name = Column(String(256))
    value = Column(DOUBLE_PRECISION)
    description = Column(Text)

    test_run = relationship('TestRun', backref=backref('metrics', passive_deletes=True))


class Request(Base):
    __tablename__ = 'requests'

    test_run_id = Column(UUID(as_uuid=True), ForeignKey('test_runs.id', ondelete='CASCADE'))
    test_id = Column(UUID(as_uuid=True))
    request_type = Column(String(128))
    timestamp = Column(DateTime)
    contents = Column(JSONB)

    test_run = relationship('TestRun', backref=backref('requests', passive_deletes=True))


class Progress(Base):
    __tablename__ = 'progress'

    test_run_id = Column(UUID(as_uuid=True), ForeignKey('test_runs.id', ondelete='CASCADE'))
    test_id = Column(UUID(as_uuid=True))
    timestamp = Column(DateTime)
    level = Column(String(10))
    message = Column(Text)
    details = Column(Text)

    test_run = relationship('TestRun', backref=backref('progress', passive_deletes=True))


class Attachment(Base):
    __tablename__ = 'attachments'

    test_run_id = Column(UUID(as_uuid=True), ForeignKey('test_runs.id', ondelete='CASCADE'))
    test_id = Column(UUID(as_uuid=True))
    timestamp = Column(DateTime)
    name = Column(String(512))
    mime_type = Column(String(128))
    size = Column(Integer)
    content = Column(BYTEA)

    test_run = relationship('TestRun', backref=backref('attachments', passive_deletes=True))


class MetricOverTime(Base):
    __tablename__ = 'metrics_over_time'
    test_run_id = Column(UUID(as_uuid=True), ForeignKey('test_runs.id', ondelete='CASCADE'))
    test_id = Column(UUID(as_uuid=True))
    name = Column(String(128))
    timestamp = Column(DateTime)
    values = Column(JSONB)

    test_run = relationship('TestRun', backref=backref('metrics_over_time', passive_deletes=True))
