"""Add indexes (*.test_run_id, test_runs.start, test_runs.project_id)

Revision ID: aae6e771fafc
Revises: 30878f8f373e
Create Date: 2023-09-10 02:35:33.670625

"""
from alembic import op
import sqlalchemy as sa
from sqlalchemy.dialects import postgresql

# revision identifiers, used by Alembic.
revision = 'aae6e771fafc'
down_revision = '30878f8f373e'
branch_labels = None
depends_on = None


def upgrade():
    op.create_index(op.f('ix_attachments_test_run_id'), 'attachments', ['test_run_id'], unique=False)
    op.create_index(op.f('ix_logs_test_run_id'), 'logs', ['test_run_id'], unique=False)
    op.create_index(op.f('ix_metrics_test_run_id'), 'metrics', ['test_run_id'], unique=False)
    op.create_index(op.f('ix_metrics_over_time_test_run_id'), 'metrics_over_time', ['test_run_id'], unique=False)
    op.create_index(op.f('ix_progress_test_run_id'), 'progress', ['test_run_id'], unique=False)
    op.create_index(op.f('ix_requests_test_run_id'), 'requests', ['test_run_id'], unique=False)
    op.create_index(op.f('ix_test_run_variants_test_run_id'), 'test_run_variants', ['test_run_id'], unique=False)
    op.create_index(op.f('ix_test_runs_project_id'), 'test_runs', ['project_id'], unique=False)
    op.create_index(op.f('ix_test_runs_start'), 'test_runs', ['start'], unique=False)
    op.create_index(op.f('ix_tests_test_run_id'), 'tests', ['test_run_id'], unique=False)


def downgrade():
    op.drop_index(op.f('ix_tests_test_run_id'), table_name='tests')
    op.drop_index(op.f('ix_test_runs_start'), table_name='test_runs')
    op.drop_index(op.f('ix_test_runs_project_id'), table_name='test_runs')
    op.drop_index(op.f('ix_test_run_variants_test_run_id'), table_name='test_run_variants')
    op.drop_index(op.f('ix_requests_test_run_id'), table_name='requests')
    op.drop_index(op.f('ix_progress_test_run_id'), table_name='progress')
    op.drop_index(op.f('ix_metrics_over_time_test_run_id'), table_name='metrics_over_time')
    op.drop_index(op.f('ix_metrics_test_run_id'), table_name='metrics')
    op.drop_index(op.f('ix_logs_test_run_id'), table_name='logs')
    op.drop_index(op.f('ix_attachments_test_run_id'), table_name='attachments')
