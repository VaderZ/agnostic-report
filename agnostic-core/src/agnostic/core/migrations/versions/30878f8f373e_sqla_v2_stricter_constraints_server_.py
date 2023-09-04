"""SQLA v2, stricter constraints, server defaults

Revision ID: 30878f8f373e
Revises: 9bbaff28298e
Create Date: 2023-08-21 01:52:15.077125

"""
import sqlalchemy as sa
from alembic import op
from sqlalchemy.dialects import postgresql

# revision identifiers, used by Alembic.
revision = '30878f8f373e'
down_revision = '9bbaff28298e'
branch_labels = None
depends_on = None


def upgrade():
    op.alter_column('attachments', 'id', server_default=sa.text('gen_random_uuid()'))
    op.alter_column('attachments', 'test_run_id',
               existing_type=sa.UUID(),
               nullable=False)
    op.alter_column('attachments', 'timestamp',
               existing_type=postgresql.TIMESTAMP(),
               nullable=False)
    op.alter_column('attachments', 'name',
               existing_type=sa.VARCHAR(length=512),
               nullable=False)
    op.alter_column('attachments', 'mime_type',
               existing_type=sa.VARCHAR(length=128),
               nullable=False)
    op.alter_column('attachments', 'size',
               existing_type=sa.INTEGER(),
               nullable=False)
    op.alter_column('attachments', 'content',
               existing_type=postgresql.BYTEA(),
               nullable=False)

    op.alter_column('logs', 'id', server_default=sa.text('gen_random_uuid()'))
    op.alter_column('logs', 'test_run_id',
               existing_type=sa.UUID(),
               nullable=False)
    op.alter_column('logs', 'name',
               existing_type=sa.VARCHAR(length=256),
               nullable=False)
    op.alter_column('logs', 'start',
               existing_type=postgresql.TIMESTAMP())
    op.alter_column('logs', 'body',
               existing_type=sa.TEXT(),
               nullable=False)

    op.alter_column('metrics', 'id', server_default=sa.text('gen_random_uuid()'))
    op.alter_column('metrics', 'test_run_id',
               existing_type=sa.UUID(),
               nullable=False)
    op.alter_column('metrics', 'timestamp',
               existing_type=postgresql.TIMESTAMP(),
               nullable=False)
    op.alter_column('metrics', 'name',
               existing_type=sa.VARCHAR(length=256),
               nullable=False)
    op.alter_column('metrics', 'value',
               existing_type=sa.DOUBLE_PRECISION(precision=53),
               nullable=False)

    # Due to client implementations it was possible to add metrics without test_run_id,
    # fix them by populating test_run_id from test details
    op.execute('''
    update metrics_over_time
    set test_run_id = tests.test_run_id
    from tests
    where metrics_over_time.test_run_id is null and metrics_over_time.test_id = tests.id
    ''')
    op.alter_column('metrics_over_time', 'id', server_default=sa.text('gen_random_uuid()'))
    op.alter_column('metrics_over_time', 'test_run_id',
               existing_type=sa.UUID(),
               nullable=False)
    op.alter_column('metrics_over_time', 'name',
               existing_type=sa.VARCHAR(length=128),
               nullable=False)
    op.alter_column('metrics_over_time', 'timestamp',
               existing_type=postgresql.TIMESTAMP(),
               nullable=False)
    op.alter_column('metrics_over_time', 'values',
               existing_type=postgresql.JSONB(astext_type=sa.Text()),
               nullable=False)

    op.alter_column('progress', 'id', server_default=sa.text('gen_random_uuid()'))
    op.alter_column('progress', 'test_run_id',
               existing_type=sa.UUID(),
               nullable=False)
    op.alter_column('progress', 'timestamp',
               existing_type=postgresql.TIMESTAMP(),
               nullable=False)
    op.alter_column('progress', 'level',
               existing_type=sa.VARCHAR(length=10),
               nullable=False)
    op.alter_column('progress', 'message',
               existing_type=sa.TEXT(),
               nullable=False)

    op.alter_column('projects', 'id', server_default=sa.text('gen_random_uuid()'))
    op.alter_column('projects', 'name',
               existing_type=sa.VARCHAR(length=256),
               nullable=False)

    op.alter_column('requests', 'id', server_default=sa.text('gen_random_uuid()'))
    op.alter_column('requests', 'test_run_id',
               existing_type=sa.UUID(),
               nullable=False)
    op.alter_column('requests', 'request_type',
               existing_type=sa.VARCHAR(length=128),
               nullable=False)
    op.alter_column('requests', 'timestamp',
               existing_type=postgresql.TIMESTAMP(),
               nullable=False)
    op.alter_column('requests', 'contents',
               existing_type=postgresql.JSONB(astext_type=sa.Text()),
               nullable=False)

    op.alter_column('test_run_variants', 'id', server_default=sa.text('gen_random_uuid()'))
    op.alter_column('test_run_variants', 'test_run_id',
               existing_type=sa.UUID(),
               nullable=False)
    op.alter_column('test_run_variants', 'name',
               existing_type=sa.VARCHAR(length=128),
               nullable=False)
    op.alter_column('test_run_variants', 'value',
               existing_type=sa.VARCHAR(length=128),
               nullable=False)

    op.alter_column('test_runs', 'id', server_default=sa.text('gen_random_uuid()'))
    op.alter_column('test_runs', 'project_id',
               existing_type=sa.UUID(),
               nullable=False)
    op.alter_column('test_runs', 'start',
               existing_type=postgresql.TIMESTAMP(),
               nullable=False)
    op.alter_column('test_runs', 'keep_forever',
               existing_type=sa.BOOLEAN(),
               nullable=False)

    op.alter_column('tests', 'id', server_default=sa.text('gen_random_uuid()'))
    op.alter_column('tests', 'test_run_id',
               existing_type=sa.UUID(),
               nullable=False)
    op.alter_column('tests', 'start',
               existing_type=postgresql.TIMESTAMP(),
               nullable=False)
    op.alter_column('tests', 'path',
               existing_type=sa.VARCHAR(length=512),
               nullable=False)
    op.alter_column('tests', 'name',
               existing_type=sa.VARCHAR(length=256),
               nullable=False)


def downgrade():
    op.alter_column('tests', 'id',  server_default=None)
    op.alter_column('tests', 'name',
               existing_type=sa.VARCHAR(length=256),
               nullable=True)
    op.alter_column('tests', 'path',
               existing_type=sa.VARCHAR(length=512),
               nullable=True)
    op.alter_column('tests', 'start',
               existing_type=postgresql.TIMESTAMP(),
               nullable=True)
    op.alter_column('tests', 'test_run_id',
               existing_type=sa.UUID(),
               nullable=True)

    op.alter_column('test_runs', 'id',  server_default=None)
    op.alter_column('test_runs', 'keep_forever',
               existing_type=sa.BOOLEAN(),
               nullable=True)
    op.alter_column('test_runs', 'start',
               existing_type=postgresql.TIMESTAMP(),
               nullable=True)
    op.alter_column('test_runs', 'project_id',
               existing_type=sa.UUID(),
               nullable=True)

    op.alter_column('test_run_variant', 'id',  server_default=None)
    op.alter_column('test_run_variants', 'value',
               existing_type=sa.VARCHAR(length=128),
               nullable=True)
    op.alter_column('test_run_variants', 'name',
               existing_type=sa.VARCHAR(length=128),
               nullable=True)
    op.alter_column('test_run_variants', 'test_run_id',
               existing_type=sa.UUID(),
               nullable=True)

    op.alter_column('requests', 'id',  server_default=None)
    op.alter_column('requests', 'contents',
               existing_type=postgresql.JSONB(astext_type=sa.Text()),
               nullable=True)
    op.alter_column('requests', 'timestamp',
               existing_type=postgresql.TIMESTAMP(),
               nullable=True)
    op.alter_column('requests', 'request_type',
               existing_type=sa.VARCHAR(length=128),
               nullable=True)
    op.alter_column('requests', 'test_run_id',
               existing_type=sa.UUID(),
               nullable=True)

    op.alter_column('projects', 'id',  server_default=None)
    op.alter_column('projects', 'name',
               existing_type=sa.VARCHAR(length=256),
               nullable=True)

    op.alter_column('progress', 'id',  server_default=None)
    op.alter_column('progress', 'message',
               existing_type=sa.TEXT(),
               nullable=True)
    op.alter_column('progress', 'level',
               existing_type=sa.VARCHAR(length=10),
               nullable=True)
    op.alter_column('progress', 'timestamp',
               existing_type=postgresql.TIMESTAMP(),
               nullable=True)
    op.alter_column('progress', 'test_run_id',
               existing_type=sa.UUID(),
               nullable=True)

    op.alter_column('metrics_over_time', 'id',  server_default=None)
    op.alter_column('metrics_over_time', 'values',
               existing_type=postgresql.JSONB(astext_type=sa.Text()),
               nullable=True)
    op.alter_column('metrics_over_time', 'timestamp',
               existing_type=postgresql.TIMESTAMP(),
               nullable=True)
    op.alter_column('metrics_over_time', 'name',
               existing_type=sa.VARCHAR(length=128),
               nullable=True)
    op.alter_column('metrics_over_time', 'test_run_id',
               existing_type=sa.UUID(),
               nullable=True)

    op.alter_column('metrics', 'id',  server_default=None)
    op.alter_column('metrics', 'value',
               existing_type=sa.DOUBLE_PRECISION(precision=53),
               nullable=True)
    op.alter_column('metrics', 'name',
               existing_type=sa.VARCHAR(length=256),
               nullable=True)
    op.alter_column('metrics', 'timestamp',
               existing_type=postgresql.TIMESTAMP(),
               nullable=True)
    op.alter_column('metrics', 'test_run_id',
               existing_type=sa.UUID(),
               nullable=True)

    op.alter_column('logs', 'id',  server_default=None)
    op.alter_column('logs', 'body',
               existing_type=sa.TEXT(),
               nullable=True)
    op.alter_column('logs', 'start',
               existing_type=postgresql.TIMESTAMP())
    op.alter_column('logs', 'name',
               existing_type=sa.VARCHAR(length=256),
               nullable=True)
    op.alter_column('logs', 'test_run_id',
               existing_type=sa.UUID(),
               nullable=True)

    op.alter_column('attachments', 'id',  server_default=None)
    op.alter_column('attachments', 'content',
               existing_type=postgresql.BYTEA(),
               nullable=True)
    op.alter_column('attachments', 'size',
               existing_type=sa.INTEGER(),
               nullable=True)
    op.alter_column('attachments', 'mime_type',
               existing_type=sa.VARCHAR(length=128),
               nullable=True)
    op.alter_column('attachments', 'name',
               existing_type=sa.VARCHAR(length=512),
               nullable=True)
    op.alter_column('attachments', 'timestamp',
               existing_type=postgresql.TIMESTAMP(),
               nullable=True)
    op.alter_column('attachments', 'test_run_id',
               existing_type=sa.UUID(),
               nullable=True)
