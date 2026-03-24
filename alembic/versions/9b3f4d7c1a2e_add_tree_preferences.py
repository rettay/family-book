"""add tree preferences

Revision ID: 9b3f4d7c1a2e
Revises: 4f3c2e1a9b7d
Create Date: 2026-03-20 09:00:00.000000
"""

from alembic import op
import sqlalchemy as sa


revision = "9b3f4d7c1a2e"
down_revision = "4f3c2e1a9b7d"
branch_labels = None
depends_on = None


def upgrade() -> None:
    op.create_table(
        "tree_preferences",
        sa.Column("id", sa.String(length=36), nullable=False),
        sa.Column("person_id", sa.String(length=36), nullable=False),
        sa.Column("display_options", sa.Text(), nullable=True, server_default="{}"),
        sa.Column("created_at", sa.DateTime(timezone=True), nullable=False),
        sa.Column("updated_at", sa.DateTime(timezone=True), nullable=False),
        sa.ForeignKeyConstraint(["person_id"], ["persons.id"], ondelete="CASCADE"),
        sa.PrimaryKeyConstraint("id"),
        sa.UniqueConstraint("person_id"),
    )


def downgrade() -> None:
    op.drop_table("tree_preferences")
