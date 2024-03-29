"""Initial schema

Revision ID: 9bbaff28298e
Revises: 
Create Date: 2022-03-25 22:51:19.217966

"""
import sqlalchemy as sa
from alembic import op
from sqlalchemy.dialects import postgresql

# revision identifiers, used by Alembic.
revision = '9bbaff28298e'
down_revision = None
branch_labels = None
depends_on = None


def upgrade():
    op.create_table('projects',
    sa.Column('id', postgresql.UUID(as_uuid=True), nullable=False),
    sa.Column('name', sa.String(length=256), nullable=True),
    sa.Column('config', postgresql.JSONB(astext_type=sa.Text()), nullable=True),
    sa.PrimaryKeyConstraint('id'),
    sa.UniqueConstraint('id'),
    sa.UniqueConstraint('name')
    )
    op.create_table('test_runs',
    sa.Column('id', postgresql.UUID(as_uuid=True), nullable=False),
    sa.Column('project_id', postgresql.UUID(as_uuid=True), nullable=True),
    sa.Column('start', sa.DateTime(), nullable=True),
    sa.Column('finish', sa.DateTime(), nullable=True),
    sa.Column('heartbeat', sa.DateTime(), nullable=True),
    sa.Column('keep_forever', sa.Boolean(), nullable=True),
    sa.Column('sut_version', sa.String(length=128), nullable=True),
    sa.Column('sut_branch', sa.String(length=128), nullable=True),
    sa.Column('test_version', sa.String(length=128), nullable=True),
    sa.Column('test_branch', sa.String(length=128), nullable=True),
    sa.Column('properties', postgresql.JSONB(astext_type=sa.Text()), nullable=True),
    sa.ForeignKeyConstraint(['project_id'], ['projects.id'], ondelete='CASCADE'),
    sa.PrimaryKeyConstraint('id'),
    sa.UniqueConstraint('id')
    )
    op.create_table('attachments',
    sa.Column('id', postgresql.UUID(as_uuid=True), nullable=False),
    sa.Column('test_run_id', postgresql.UUID(as_uuid=True), nullable=True),
    sa.Column('test_id', postgresql.UUID(as_uuid=True), nullable=True),
    sa.Column('timestamp', sa.DateTime(), nullable=True),
    sa.Column('name', sa.String(length=512), nullable=True),
    sa.Column('mime_type', sa.String(length=128), nullable=True),
    sa.Column('size', sa.Integer(), nullable=True),
    sa.Column('content', postgresql.BYTEA(), nullable=True),
    sa.ForeignKeyConstraint(['test_run_id'], ['test_runs.id'], ondelete='CASCADE'),
    sa.PrimaryKeyConstraint('id'),
    sa.UniqueConstraint('id')
    )
    op.create_table('logs',
    sa.Column('id', postgresql.UUID(as_uuid=True), nullable=False),
    sa.Column('test_run_id', postgresql.UUID(as_uuid=True), nullable=True),
    sa.Column('test_id', postgresql.UUID(as_uuid=True), nullable=True),
    sa.Column('name', sa.String(length=256), nullable=True),
    sa.Column('start', sa.DateTime(), nullable=True),
    sa.Column('finish', sa.DateTime(), nullable=True),
    sa.Column('body', sa.Text(), nullable=True),
    sa.ForeignKeyConstraint(['test_run_id'], ['test_runs.id'], ondelete='CASCADE'),
    sa.PrimaryKeyConstraint('id'),
    sa.UniqueConstraint('id')
    )
    op.create_table('metrics',
    sa.Column('id', postgresql.UUID(as_uuid=True), nullable=False),
    sa.Column('test_run_id', postgresql.UUID(as_uuid=True), nullable=True),
    sa.Column('test_id', postgresql.UUID(as_uuid=True), nullable=True),
    sa.Column('timestamp', sa.DateTime(), nullable=True),
    sa.Column('name', sa.String(length=256), nullable=True),
    sa.Column('value', postgresql.DOUBLE_PRECISION(), nullable=True),
    sa.Column('description', sa.Text(), nullable=True),
    sa.ForeignKeyConstraint(['test_run_id'], ['test_runs.id'], ondelete='CASCADE'),
    sa.PrimaryKeyConstraint('id'),
    sa.UniqueConstraint('id')
    )
    op.create_table('metrics_over_time',
    sa.Column('id', postgresql.UUID(as_uuid=True), nullable=False),
    sa.Column('test_run_id', postgresql.UUID(as_uuid=True), nullable=True),
    sa.Column('test_id', postgresql.UUID(as_uuid=True), nullable=True),
    sa.Column('name', sa.String(length=128), nullable=True),
    sa.Column('timestamp', sa.DateTime(), nullable=True),
    sa.Column('values', postgresql.JSONB(astext_type=sa.Text()), nullable=True),
    sa.ForeignKeyConstraint(['test_run_id'], ['test_runs.id'], ondelete='CASCADE'),
    sa.PrimaryKeyConstraint('id'),
    sa.UniqueConstraint('id')
    )
    op.create_table('progress',
    sa.Column('id', postgresql.UUID(as_uuid=True), nullable=False),
    sa.Column('test_run_id', postgresql.UUID(as_uuid=True), nullable=True),
    sa.Column('test_id', postgresql.UUID(as_uuid=True), nullable=True),
    sa.Column('timestamp', sa.DateTime(), nullable=True),
    sa.Column('level', sa.String(length=10), nullable=True),
    sa.Column('message', sa.Text(), nullable=True),
    sa.Column('details', sa.Text(), nullable=True),
    sa.ForeignKeyConstraint(['test_run_id'], ['test_runs.id'], ondelete='CASCADE'),
    sa.PrimaryKeyConstraint('id'),
    sa.UniqueConstraint('id')
    )
    op.create_table('requests',
    sa.Column('id', postgresql.UUID(as_uuid=True), nullable=False),
    sa.Column('test_run_id', postgresql.UUID(as_uuid=True), nullable=True),
    sa.Column('test_id', postgresql.UUID(as_uuid=True), nullable=True),
    sa.Column('request_type', sa.String(length=128), nullable=True),
    sa.Column('timestamp', sa.DateTime(), nullable=True),
    sa.Column('contents', postgresql.JSONB(astext_type=sa.Text()), nullable=True),
    sa.ForeignKeyConstraint(['test_run_id'], ['test_runs.id'], ondelete='CASCADE'),
    sa.PrimaryKeyConstraint('id'),
    sa.UniqueConstraint('id')
    )
    op.create_table('test_run_variants',
    sa.Column('id', postgresql.UUID(as_uuid=True), nullable=False),
    sa.Column('test_run_id', postgresql.UUID(as_uuid=True), nullable=True),
    sa.Column('name', sa.String(length=128), nullable=True),
    sa.Column('value', sa.String(length=128), nullable=True),
    sa.ForeignKeyConstraint(['test_run_id'], ['test_runs.id'], ondelete='CASCADE'),
    sa.PrimaryKeyConstraint('id'),
    sa.UniqueConstraint('id'),
    sa.UniqueConstraint('test_run_id', 'name', name='unique_tr_variant')
    )
    op.create_table('tests',
    sa.Column('id', postgresql.UUID(as_uuid=True), nullable=False),
    sa.Column('test_run_id', postgresql.UUID(as_uuid=True), nullable=True),
    sa.Column('start', sa.DateTime(), nullable=True),
    sa.Column('finish', sa.DateTime(), nullable=True),
    sa.Column('path', sa.String(length=512), nullable=True),
    sa.Column('name', sa.String(length=256), nullable=True),
    sa.Column('result', sa.String(length=8), nullable=True),
    sa.Column('reason', sa.Text(), nullable=True),
    sa.Column('error_message', sa.Text(), nullable=True),
    sa.Column('description', sa.Text(), nullable=True),
    sa.CheckConstraint("result IN (NULL, 'passed', 'failed', 'skipped', 'xpassed', 'xfailed')", name='check_test_result'),
    sa.ForeignKeyConstraint(['test_run_id'], ['test_runs.id'], ondelete='CASCADE'),
    sa.PrimaryKeyConstraint('id'),
    sa.UniqueConstraint('id')
    )


def downgrade():
    op.drop_table('tests')
    op.drop_table('test_run_variants')
    op.drop_table('requests')
    op.drop_table('progress')
    op.drop_table('metrics_over_time')
    op.drop_table('metrics')
    op.drop_table('logs')
    op.drop_table('attachments')
    op.drop_table('test_runs')
    op.drop_table('projects')
