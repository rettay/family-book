"""add_research_notes_to_person

Revision ID: 74a687671a40
Revises: b4d3e9a1c2f0
Create Date: 2026-03-25 18:30:34.572664

"""
from typing import Sequence, Union

from alembic import op
import sqlalchemy as sa


# revision identifiers, used by Alembic.
revision: str = '74a687671a40'
down_revision: Union[str, Sequence[str], None] = 'b4d3e9a1c2f0'
branch_labels: Union[str, Sequence[str], None] = None
depends_on: Union[str, Sequence[str], None] = None


def upgrade() -> None:
    """Upgrade schema."""
    with op.batch_alter_table('persons', schema=None) as batch_op:
        batch_op.add_column(sa.Column('research_notes', sa.Text(), nullable=True))


def downgrade() -> None:
    """Downgrade schema."""
    with op.batch_alter_table('persons', schema=None) as batch_op:
        batch_op.drop_column('research_notes')
