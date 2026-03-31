"""add place_history column to persons

Revision ID: d60183d4b818
Revises: c3d4e5f6a7b8
Create Date: 2026-03-31 14:53:49.569433

"""
from typing import Sequence, Union

from alembic import op
import sqlalchemy as sa


# revision identifiers, used by Alembic.
revision: str = 'd60183d4b818'
down_revision: Union[str, Sequence[str], None] = 'c3d4e5f6a7b8'
branch_labels: Union[str, Sequence[str], None] = None
depends_on: Union[str, Sequence[str], None] = None


def upgrade() -> None:
    """Upgrade schema."""
    with op.batch_alter_table('persons', schema=None) as batch_op:
        batch_op.add_column(sa.Column('place_history', sa.Text(), nullable=True))


def downgrade() -> None:
    """Downgrade schema."""
    with op.batch_alter_table('persons', schema=None) as batch_op:
        batch_op.drop_column('place_history')
