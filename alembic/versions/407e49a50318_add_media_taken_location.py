"""add_media_taken_location

Revision ID: 407e49a50318
Revises: 6ece7cae8ff0
Create Date: 2026-04-05 22:31:10.749416

"""
from typing import Sequence, Union

from alembic import op
import sqlalchemy as sa


# revision identifiers, used by Alembic.
revision: str = '407e49a50318'
down_revision: Union[str, Sequence[str], None] = '6ece7cae8ff0'
branch_labels: Union[str, Sequence[str], None] = None
depends_on: Union[str, Sequence[str], None] = None


def upgrade() -> None:
    """Upgrade schema."""
    with op.batch_alter_table("media") as batch_op:
        batch_op.add_column(sa.Column("taken_location", sa.String(500), nullable=True))


def downgrade() -> None:
    """Downgrade schema."""
    with op.batch_alter_table("media") as batch_op:
        batch_op.drop_column("taken_location")
