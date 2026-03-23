"""add burial country code

Revision ID: c6a8d41f2b5e
Revises: 9b3f4d7c1a2e
Create Date: 2026-03-23 13:15:00.000000
"""

from alembic import op
import sqlalchemy as sa


revision = "c6a8d41f2b5e"
down_revision = "9b3f4d7c1a2e"
branch_labels = None
depends_on = None


def upgrade() -> None:
    with op.batch_alter_table("persons") as batch_op:
        batch_op.add_column(sa.Column("burial_country_code", sa.String(length=2), nullable=True))


def downgrade() -> None:
    with op.batch_alter_table("persons") as batch_op:
        batch_op.drop_column("burial_country_code")
