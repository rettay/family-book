"""add onboarding and media inbox tables

Revision ID: a6d9f3b1c2e4
Revises: f1a2b3c4d5e6
Create Date: 2026-04-09 03:00:00.000000
"""

from typing import Sequence, Union

from alembic import op
import sqlalchemy as sa


revision: str = "a6d9f3b1c2e4"
down_revision: Union[str, Sequence[str], None] = "f1a2b3c4d5e6"
branch_labels: Union[str, Sequence[str], None] = None
depends_on: Union[str, Sequence[str], None] = None


def upgrade() -> None:
    op.create_table(
        "onboarding_progress",
        sa.Column("id", sa.String(length=36), nullable=False),
        sa.Column("person_id", sa.String(length=36), nullable=False),
        sa.Column("status", sa.String(length=20), nullable=False),
        sa.Column("selected_path", sa.String(length=20), nullable=True),
        sa.Column("milestones", sa.Text(), nullable=True),
        sa.Column("started_at", sa.DateTime(), nullable=False),
        sa.Column("completed_at", sa.DateTime(), nullable=True),
        sa.Column("skipped_at", sa.DateTime(), nullable=True),
        sa.Column("updated_at", sa.DateTime(), nullable=False),
        sa.ForeignKeyConstraint(["person_id"], ["persons.id"], ondelete="CASCADE"),
        sa.PrimaryKeyConstraint("id"),
        sa.UniqueConstraint("person_id"),
    )
    op.create_index(
        op.f("ix_onboarding_progress_person_id"),
        "onboarding_progress",
        ["person_id"],
        unique=True,
    )

    op.create_table(
        "media_inbox_items",
        sa.Column("id", sa.String(length=36), nullable=False),
        sa.Column("file_path", sa.String(length=500), nullable=False),
        sa.Column("original_filename", sa.String(length=300), nullable=True),
        sa.Column("mime_type", sa.String(length=50), nullable=True),
        sa.Column("file_size_bytes", sa.Integer(), nullable=True),
        sa.Column("file_hash", sa.String(length=64), nullable=True),
        sa.Column("media_type", sa.String(length=20), nullable=False),
        sa.Column("status", sa.String(length=20), nullable=False),
        sa.Column("uploaded_by", sa.String(length=36), nullable=False),
        sa.Column("attached_media_id", sa.String(length=36), nullable=True),
        sa.Column("attached_person_id", sa.String(length=36), nullable=True),
        sa.Column("source_title", sa.String(length=300), nullable=True),
        sa.Column("source_text", sa.Text(), nullable=True),
        sa.Column("title", sa.String(length=300), nullable=True),
        sa.Column("caption", sa.String(length=1000), nullable=True),
        sa.Column("taken_date", sa.String(length=10), nullable=True),
        sa.Column("taken_location", sa.String(length=500), nullable=True),
        sa.Column("tagged_person_ids", sa.Text(), nullable=True),
        sa.Column("created_at", sa.DateTime(), nullable=False),
        sa.Column("updated_at", sa.DateTime(), nullable=False),
        sa.ForeignKeyConstraint(["uploaded_by"], ["persons.id"], ondelete="CASCADE"),
        sa.PrimaryKeyConstraint("id"),
    )
    op.create_index(
        "idx_media_inbox_status_created_at",
        "media_inbox_items",
        ["status", "created_at"],
        unique=False,
    )


def downgrade() -> None:
    op.drop_index("idx_media_inbox_status_created_at", table_name="media_inbox_items")
    op.drop_table("media_inbox_items")
    op.drop_index(op.f("ix_onboarding_progress_person_id"), table_name="onboarding_progress")
    op.drop_table("onboarding_progress")
