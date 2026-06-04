"""Initial migration: ingestion_jobs table

Revision ID: 20250604_000000
Revises:
Create Date: 2026-06-04 00:00:00.000000+03:00

"""
from typing import Sequence, Union

from alembic import op
import sqlalchemy as sa
from sqlalchemy.dialects import postgresql

# revision identifiers, used by Alembic.
revision: str = "20250604_000000"
down_revision: Union[str, None] = None
branch_labels: Union[str, Sequence[str], None] = None
depends_on: Union[str, Sequence[str], None] = None


def upgrade() -> None:
    op.create_table(
        "ingestion_jobs",
        sa.Column("id", postgresql.UUID(as_uuid=True), primary_key=True),
        sa.Column("book_title", sa.String(255), nullable=False, index=True),
        sa.Column("source_type", sa.String(50), nullable=False, default="sefaria"),
        sa.Column(
            "status",
            sa.Enum("pending", "running", "completed", "failed", "cancelled", name="jobstatus"),
            nullable=False,
            index=True,
        ),
        sa.Column("total_refs", sa.Integer(), nullable=True),
        sa.Column("fetched_refs", sa.Integer(), nullable=True, default=0),
        sa.Column("failed_refs", sa.Integer(), nullable=True, default=0),
        sa.Column("errors", postgresql.JSONB(), nullable=True, default=list),
        sa.Column("meta", postgresql.JSONB(), nullable=True, default=dict),
        sa.Column(
            "created_at",
            sa.DateTime(timezone=True),
            server_default=sa.func.now(),
        ),
        sa.Column(
            "updated_at",
            sa.DateTime(timezone=True),
            server_default=sa.func.now(),
            onupdate=sa.func.now(),
        ),
    )


def downgrade() -> None:
    op.drop_table("ingestion_jobs")
    op.execute("DROP TYPE IF EXISTS jobstatus")
