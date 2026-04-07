"""add person_occupations table

Revision ID: a3c7f2e8b1d4
Revises: 407e49a50318
Create Date: 2026-04-06 12:00:00.000000

"""
from typing import Sequence, Union

from alembic import op
import sqlalchemy as sa


revision: str = "a3c7f2e8b1d4"
down_revision: Union[str, None] = "407e49a50318"
branch_labels: Union[str, Sequence[str], None] = None
depends_on: Union[str, Sequence[str], None] = None


def upgrade() -> None:
    op.create_table(
        "person_occupations",
        sa.Column("id", sa.String(36), primary_key=True),
        sa.Column("person_id", sa.String(36), sa.ForeignKey("persons.id", ondelete="CASCADE"), nullable=False),
        sa.Column("title", sa.Text, nullable=False),
        sa.Column("employer", sa.Text, nullable=True),
        sa.Column("start_date", sa.String(100), nullable=True),
        sa.Column("end_date", sa.String(100), nullable=True),
        sa.Column("added_by_person_id", sa.String(36), sa.ForeignKey("persons.id", ondelete="SET NULL"), nullable=True),
        sa.Column("source", sa.Text, nullable=True),
        sa.Column("created_at", sa.DateTime, nullable=False),
        sa.Column("updated_at", sa.DateTime, nullable=False),
    )
    op.create_index("ix_person_occupations_person_id", "person_occupations", ["person_id"])


def downgrade() -> None:
    op.drop_index("ix_person_occupations_person_id", table_name="person_occupations")
    op.drop_table("person_occupations")
