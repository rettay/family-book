"""add_physical_genetic_medical_fields

Revision ID: 9dc8ffc2dc25
Revises: 91c60b8a16f9
Create Date: 2026-03-26 11:14:37.010839

"""
from typing import Sequence, Union

from alembic import op
import sqlalchemy as sa


# revision identifiers, used by Alembic.
revision: str = '9dc8ffc2dc25'
down_revision: Union[str, Sequence[str], None] = '91c60b8a16f9'
branch_labels: Union[str, Sequence[str], None] = None
depends_on: Union[str, Sequence[str], None] = None


def upgrade() -> None:
    """Upgrade schema."""
    with op.batch_alter_table('persons', schema=None) as batch_op:
        batch_op.add_column(sa.Column('height', sa.String(length=50), nullable=True))
        batch_op.add_column(sa.Column('weight', sa.String(length=50), nullable=True))
        batch_op.add_column(sa.Column('eye_color', sa.String(length=50), nullable=True))
        batch_op.add_column(sa.Column('hair_color', sa.String(length=50), nullable=True))
        batch_op.add_column(sa.Column('blood_type', sa.String(length=10), nullable=True))
        batch_op.add_column(sa.Column('maternal_haplogroup', sa.Text(), nullable=True))
        batch_op.add_column(sa.Column('paternal_haplogroup', sa.Text(), nullable=True))
        batch_op.add_column(sa.Column('dna_test_provider', sa.Text(), nullable=True))
        batch_op.add_column(sa.Column('admixture', sa.Text(), nullable=True))
        batch_op.add_column(sa.Column('medical_conditions', sa.Text(), nullable=True))


def downgrade() -> None:
    """Downgrade schema."""
    with op.batch_alter_table('persons', schema=None) as batch_op:
        batch_op.drop_column('medical_conditions')
        batch_op.drop_column('admixture')
        batch_op.drop_column('dna_test_provider')
        batch_op.drop_column('paternal_haplogroup')
        batch_op.drop_column('maternal_haplogroup')
        batch_op.drop_column('blood_type')
        batch_op.drop_column('hair_color')
        batch_op.drop_column('eye_color')
        batch_op.drop_column('weight')
        batch_op.drop_column('height')
