"""add sensitive field encryption support

Revision ID: 8c1f9e6b7d11
Revises: f3c4b8e1a9d2
Create Date: 2026-03-24 00:00:00.000000
"""

from collections.abc import Sequence

import sqlalchemy as sa
from alembic import op


revision: str = "8c1f9e6b7d11"
down_revision: str | None = "f3c4b8e1a9d2"
branch_labels: str | Sequence[str] | None = None
depends_on: str | Sequence[str] | None = None


def upgrade() -> None:
    with op.batch_alter_table("persons") as batch_op:
        batch_op.alter_column("medical_history", existing_type=sa.Text(), type_=sa.Text(), existing_nullable=True)
        batch_op.alter_column("contact_whatsapp", existing_type=sa.String(length=20), type_=sa.Text(), existing_nullable=True)
        batch_op.alter_column("contact_telegram", existing_type=sa.String(length=100), type_=sa.Text(), existing_nullable=True)
        batch_op.alter_column("contact_signal", existing_type=sa.String(length=20), type_=sa.Text(), existing_nullable=True)
        batch_op.alter_column("contact_email", existing_type=sa.String(length=320), type_=sa.Text(), existing_nullable=True)
        batch_op.add_column(sa.Column("contact_email_hash", sa.String(length=64), nullable=True))
        batch_op.create_index("idx_persons_contact_email_hash", ["contact_email_hash"], unique=False)


def downgrade() -> None:
    with op.batch_alter_table("persons") as batch_op:
        batch_op.drop_index("idx_persons_contact_email_hash")
        batch_op.drop_column("contact_email_hash")
        batch_op.alter_column("contact_email", existing_type=sa.Text(), type_=sa.String(length=320), existing_nullable=True)
        batch_op.alter_column("contact_signal", existing_type=sa.Text(), type_=sa.String(length=20), existing_nullable=True)
        batch_op.alter_column("contact_telegram", existing_type=sa.Text(), type_=sa.String(length=100), existing_nullable=True)
        batch_op.alter_column("contact_whatsapp", existing_type=sa.Text(), type_=sa.String(length=20), existing_nullable=True)
        batch_op.alter_column("medical_history", existing_type=sa.Text(), type_=sa.Text(), existing_nullable=True)
