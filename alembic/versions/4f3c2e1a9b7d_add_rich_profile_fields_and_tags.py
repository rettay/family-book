"""add rich profile fields and tagging support

Revision ID: 4f3c2e1a9b7d
Revises: 2e7d8d8d6d4b
Create Date: 2026-03-19 18:00:00.000000
"""

from alembic import op
import sqlalchemy as sa


revision = "4f3c2e1a9b7d"
down_revision = "2e7d8d8d6d4b"
branch_labels = None
depends_on = None


def upgrade() -> None:
    with op.batch_alter_table("persons") as batch_op:
        batch_op.add_column(sa.Column("burial_cemetery_name", sa.String(length=300), nullable=True))
        batch_op.add_column(sa.Column("burial_plot_number", sa.String(length=100), nullable=True))
        batch_op.add_column(sa.Column("medical_history", sa.Text(), nullable=True))

    with op.batch_alter_table("media") as batch_op:
        batch_op.add_column(sa.Column("tagged_person_ids", sa.Text(), nullable=True, server_default="[]"))

    with op.batch_alter_table("moments") as batch_op:
        batch_op.add_column(sa.Column("tagged_person_ids", sa.Text(), nullable=True, server_default="[]"))


def downgrade() -> None:
    with op.batch_alter_table("moments") as batch_op:
        batch_op.drop_column("tagged_person_ids")

    with op.batch_alter_table("media") as batch_op:
        batch_op.drop_column("tagged_person_ids")

    with op.batch_alter_table("persons") as batch_op:
        batch_op.drop_column("medical_history")
        batch_op.drop_column("burial_plot_number")
        batch_op.drop_column("burial_cemetery_name")
