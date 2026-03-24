"""add app theme settings

Revision ID: b4d3e9a1c2f0
Revises: 8c1f9e6b7d11
Create Date: 2026-03-25 00:00:00.000000
"""

from collections.abc import Sequence

import sqlalchemy as sa
from alembic import op


revision: str = "b4d3e9a1c2f0"
down_revision: str | None = "8c1f9e6b7d11"
branch_labels: str | Sequence[str] | None = None
depends_on: str | Sequence[str] | None = None


def upgrade() -> None:
    op.create_table(
        "app_theme_settings",
        sa.Column("id", sa.String(length=36), nullable=False),
        sa.Column("singleton_key", sa.String(length=32), nullable=False),
        sa.Column("settings_json", sa.Text(), nullable=True),
        sa.Column("created_at", sa.DateTime(), nullable=False),
        sa.Column("updated_at", sa.DateTime(), nullable=False),
        sa.PrimaryKeyConstraint("id"),
        sa.UniqueConstraint("singleton_key"),
    )


def downgrade() -> None:
    op.drop_table("app_theme_settings")
