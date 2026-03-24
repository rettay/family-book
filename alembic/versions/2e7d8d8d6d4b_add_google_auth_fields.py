"""add google auth fields

Revision ID: 2e7d8d8d6d4b
Revises: 75d48eb17ca2
Create Date: 2026-03-19 10:05:00.000000
"""

from alembic import op
import sqlalchemy as sa


revision = "2e7d8d8d6d4b"
down_revision = "75d48eb17ca2"
branch_labels = None
depends_on = None


def upgrade() -> None:
    op.add_column("persons", sa.Column("google_sub", sa.String(length=255), nullable=True))
    op.add_column("persons", sa.Column("google_email", sa.String(length=320), nullable=True))
    op.create_index(
        "idx_persons_google_sub",
        "persons",
        ["google_sub"],
        unique=True,
        sqlite_where=sa.text("google_sub IS NOT NULL"),
    )


def downgrade() -> None:
    op.drop_index("idx_persons_google_sub", table_name="persons")
    op.drop_column("persons", "google_email")
    op.drop_column("persons", "google_sub")
