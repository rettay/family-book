"""add revisions and recoverable state

Revision ID: f3c4b8e1a9d2
Revises: c6a8d41f2b5e
Create Date: 2026-03-24 10:30:00.000000
"""

from alembic import op
import sqlalchemy as sa


revision = "f3c4b8e1a9d2"
down_revision = "c6a8d41f2b5e"
branch_labels = None
depends_on = None


def upgrade() -> None:
    with op.batch_alter_table("persons") as batch_op:
        batch_op.add_column(
            sa.Column("lifecycle_state", sa.String(length=20), nullable=False, server_default="active")
        )
        batch_op.add_column(sa.Column("deleted_at", sa.String(length=40), nullable=True))
        batch_op.add_column(sa.Column("deleted_by", sa.String(length=36), nullable=True))

    with op.batch_alter_table("moments") as batch_op:
        batch_op.add_column(
            sa.Column("lifecycle_state", sa.String(length=20), nullable=False, server_default="active")
        )
        batch_op.add_column(sa.Column("moderated_at", sa.DateTime(), nullable=True))
        batch_op.add_column(sa.Column("moderated_by", sa.String(length=36), nullable=True))
        batch_op.add_column(sa.Column("moderation_reason", sa.String(length=500), nullable=True))
        batch_op.add_column(sa.Column("deleted_at", sa.DateTime(), nullable=True))
        batch_op.add_column(sa.Column("deleted_by", sa.String(length=36), nullable=True))

    op.create_table(
        "entity_revisions",
        sa.Column("id", sa.String(length=36), nullable=False),
        sa.Column("entity_type", sa.String(length=30), nullable=False),
        sa.Column("entity_id", sa.String(length=36), nullable=False),
        sa.Column("actor_id", sa.String(length=36), nullable=True),
        sa.Column("action", sa.String(length=30), nullable=False),
        sa.Column("snapshot", sa.Text(), nullable=False),
        sa.Column("created_at", sa.DateTime(), nullable=False),
        sa.PrimaryKeyConstraint("id"),
    )


def downgrade() -> None:
    op.drop_table("entity_revisions")

    with op.batch_alter_table("moments") as batch_op:
        batch_op.drop_column("deleted_by")
        batch_op.drop_column("deleted_at")
        batch_op.drop_column("moderation_reason")
        batch_op.drop_column("moderated_by")
        batch_op.drop_column("moderated_at")
        batch_op.drop_column("lifecycle_state")

    with op.batch_alter_table("persons") as batch_op:
        batch_op.drop_column("deleted_by")
        batch_op.drop_column("deleted_at")
        batch_op.drop_column("lifecycle_state")
