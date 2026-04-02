"""add richer person editor identity and contact fields

Revision ID: a1b2c3d4e5f6
Revises: f7a9b3c1d4e2
Create Date: 2026-03-30 00:20:00.000000
"""

from alembic import op
import sqlalchemy as sa


# revision identifiers, used by Alembic.
revision = "a1b2c3d4e5f6"
down_revision = "f7a9b3c1d4e2"
branch_labels = None
depends_on = None


def upgrade() -> None:
    op.add_column("persons", sa.Column("alternate_nicknames", sa.Text(), nullable=True))
    op.add_column("persons", sa.Column("remains_disposition", sa.String(length=20), nullable=True))
    op.add_column("persons", sa.Column("contact_phone", sa.Text(), nullable=True))
    op.add_column("persons", sa.Column("contact_addresses", sa.Text(), nullable=True))


def downgrade() -> None:
    op.drop_column("persons", "contact_addresses")
    op.drop_column("persons", "contact_phone")
    op.drop_column("persons", "remains_disposition")
    op.drop_column("persons", "alternate_nicknames")
