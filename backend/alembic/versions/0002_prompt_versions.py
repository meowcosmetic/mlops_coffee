"""prompt versions

Revision ID: 0002
Revises: 0001
Create Date: 2026-09-16

"""
from alembic import op
import sqlalchemy as sa

revision = "0002"
down_revision = "0001"
branch_labels = None
depends_on = None


def upgrade() -> None:
    op.create_table(
        "prompt_versions",
        sa.Column("id", sa.Integer(), primary_key=True),
        sa.Column("name", sa.String(100), nullable=False),
        sa.Column("version", sa.String(20), nullable=False),
        sa.Column("template", sa.Text(), nullable=False),
        sa.Column("prompt_hash", sa.String(64), nullable=False),
        sa.Column("is_active", sa.Boolean(), nullable=False, server_default=sa.false()),
        sa.Column("created_at", sa.DateTime(timezone=True), server_default=sa.func.now()),
        sa.UniqueConstraint("name", "version", name="uq_prompt_name_version"),
    )
    op.create_index("ix_prompt_versions_name", "prompt_versions", ["name"])


def downgrade() -> None:
    op.drop_index("ix_prompt_versions_name", table_name="prompt_versions")
    op.drop_table("prompt_versions")
