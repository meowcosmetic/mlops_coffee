"""pending preference changes

Revision ID: 0003
Revises: 0002
Create Date: 2026-09-16

"""
from alembic import op
import sqlalchemy as sa

revision = "0003"
down_revision = "0002"
branch_labels = None
depends_on = None


def upgrade() -> None:
    op.create_table(
        "pending_preference_changes",
        sa.Column("id", sa.Integer(), primary_key=True),
        sa.Column("user_id", sa.Integer(), sa.ForeignKey("users.id"), nullable=False),
        sa.Column("changes", sa.JSON(), nullable=False),
        sa.Column("status", sa.String(20), nullable=False, server_default="pending"),
        sa.Column("created_at", sa.DateTime(timezone=True), server_default=sa.func.now()),
    )
    op.create_index("ix_pending_preference_changes_user_id", "pending_preference_changes", ["user_id"])


def downgrade() -> None:
    op.drop_index("ix_pending_preference_changes_user_id", table_name="pending_preference_changes")
    op.drop_table("pending_preference_changes")
