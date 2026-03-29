"""add person location coordinates

Revision ID: f7a9b3c1d4e2
Revises: e2a9d4f6c8b1
Create Date: 2026-03-28 23:20:00.000000
"""

from alembic import op
import sqlalchemy as sa


# revision identifiers, used by Alembic.
revision = "f7a9b3c1d4e2"
down_revision = "e2a9d4f6c8b1"
branch_labels = None
depends_on = None


def upgrade() -> None:
    op.add_column("persons", sa.Column("birth_place_latitude", sa.Float(), nullable=True))
    op.add_column("persons", sa.Column("birth_place_longitude", sa.Float(), nullable=True))
    op.add_column("persons", sa.Column("residence_place_latitude", sa.Float(), nullable=True))
    op.add_column("persons", sa.Column("residence_place_longitude", sa.Float(), nullable=True))
    op.add_column("persons", sa.Column("burial_place_latitude", sa.Float(), nullable=True))
    op.add_column("persons", sa.Column("burial_place_longitude", sa.Float(), nullable=True))


def downgrade() -> None:
    op.drop_column("persons", "burial_place_longitude")
    op.drop_column("persons", "burial_place_latitude")
    op.drop_column("persons", "residence_place_longitude")
    op.drop_column("persons", "residence_place_latitude")
    op.drop_column("persons", "birth_place_longitude")
    op.drop_column("persons", "birth_place_latitude")
