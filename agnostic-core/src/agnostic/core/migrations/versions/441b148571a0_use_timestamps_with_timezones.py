"""Use timestamps with timezones

Revision ID: 441b148571a0
Revises: aae6e771fafc
Create Date: 2023-09-23 02:51:38.259829

"""
from alembic import op
import sqlalchemy as sa
from sqlalchemy.dialects import postgresql


# revision identifiers, used by Alembic.
revision = '441b148571a0'
down_revision = 'aae6e771fafc'
branch_labels = None
depends_on = None


def upgrade():
    op.alter_column('attachments', 'timestamp', type_=postgresql.TIMESTAMP(timezone=True))
    op.alter_column("logs", "start", type_=postgresql.TIMESTAMP(timezone=True))
    op.alter_column("logs", "finish", type_=postgresql.TIMESTAMP(timezone=True))
    op.alter_column("metrics", "timestamp", type_=postgresql.TIMESTAMP(timezone=True))
    op.alter_column("metrics_over_time", "timestamp", type_=postgresql.TIMESTAMP(timezone=True))
    op.alter_column("progress", "timestamp", type_=postgresql.TIMESTAMP(timezone=True))
    op.alter_column("requests", "timestamp", type_=postgresql.TIMESTAMP(timezone=True))
    op.alter_column("test_runs", "start", type_=postgresql.TIMESTAMP(timezone=True))
    op.alter_column("test_runs", "finish", type_=postgresql.TIMESTAMP(timezone=True))
    op.alter_column("test_runs", "heartbeat", type_=postgresql.TIMESTAMP(timezone=True))
    op.alter_column("tests", "start", type_=postgresql.TIMESTAMP(timezone=True))
    op.alter_column("tests", "finish", type_=postgresql.TIMESTAMP(timezone=True))


def downgrade():
    op.alter_column('attachments', 'timestamp', type_=postgresql.TIMESTAMP)
    op.alter_column("logs", "start", type_=postgresql.TIMESTAMP)
    op.alter_column("logs", "finish", type_=postgresql.TIMESTAMP)
    op.alter_column("metrics", "timestamp", type_=postgresql.TIMESTAMP)
    op.alter_column("metrics_over_time", "timestamp", type_=postgresql.TIMESTAMP)
    op.alter_column("progress", "timestamp", type_=postgresql.TIMESTAMP)
    op.alter_column("requests", "timestamp", type_=postgresql.TIMESTAMP)
    op.alter_column("test_runs", "start", type_=postgresql.TIMESTAMP)
    op.alter_column("test_runs", "finish", type_=postgresql.TIMESTAMP)
    op.alter_column("test_runs", "heartbeat", type_=postgresql.TIMESTAMP)
    op.alter_column("tests", "start", type_=postgresql.TIMESTAMP)
    op.alter_column("tests", "finish", type_=postgresql.TIMESTAMP)
