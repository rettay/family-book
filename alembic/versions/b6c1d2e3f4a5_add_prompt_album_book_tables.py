"""add prompt, album, and book tables

Revision ID: b6c1d2e3f4a5
Revises: a6d9f3b1c2e4
Create Date: 2026-04-10 12:00:00.000000
"""

from typing import Sequence, Union

from alembic import op
import sqlalchemy as sa


revision: str = "b6c1d2e3f4a5"
down_revision: Union[str, Sequence[str], None] = "a6d9f3b1c2e4"
branch_labels: Union[str, Sequence[str], None] = None
depends_on: Union[str, Sequence[str], None] = None


def upgrade() -> None:
    op.create_table(
        "prompt_campaigns",
        sa.Column("id", sa.String(length=36), nullable=False),
        sa.Column("created_by", sa.String(length=36), nullable=False),
        sa.Column("target_person_id", sa.String(length=36), nullable=True),
        sa.Column("title", sa.String(length=300), nullable=False),
        sa.Column("prompt_body", sa.Text(), nullable=False),
        sa.Column("response_kind", sa.String(length=20), nullable=False),
        sa.Column("status", sa.String(length=20), nullable=False),
        sa.Column("due_date", sa.String(length=10), nullable=True),
        sa.Column("sent_at", sa.DateTime(), nullable=False),
        sa.Column("created_at", sa.DateTime(), nullable=False),
        sa.Column("updated_at", sa.DateTime(), nullable=False),
        sa.ForeignKeyConstraint(["created_by"], ["persons.id"], ondelete="CASCADE"),
        sa.ForeignKeyConstraint(["target_person_id"], ["persons.id"], ondelete="SET NULL"),
        sa.PrimaryKeyConstraint("id"),
    )
    op.create_table(
        "prompt_campaign_recipients",
        sa.Column("id", sa.String(length=36), nullable=False),
        sa.Column("campaign_id", sa.String(length=36), nullable=False),
        sa.Column("recipient_person_id", sa.String(length=36), nullable=False),
        sa.Column("status", sa.String(length=20), nullable=False),
        sa.Column("response_story_id", sa.String(length=36), nullable=True),
        sa.Column("response_inbox_item_id", sa.String(length=36), nullable=True),
        sa.Column("response_excerpt", sa.Text(), nullable=True),
        sa.Column("responded_at", sa.DateTime(), nullable=True),
        sa.Column("created_at", sa.DateTime(), nullable=False),
        sa.ForeignKeyConstraint(["campaign_id"], ["prompt_campaigns.id"], ondelete="CASCADE"),
        sa.ForeignKeyConstraint(["recipient_person_id"], ["persons.id"], ondelete="CASCADE"),
        sa.PrimaryKeyConstraint("id"),
        sa.UniqueConstraint("campaign_id", "recipient_person_id", name="uq_prompt_campaign_recipient"),
    )
    op.create_table(
        "albums",
        sa.Column("id", sa.String(length=36), nullable=False),
        sa.Column("title", sa.String(length=300), nullable=False),
        sa.Column("description", sa.Text(), nullable=True),
        sa.Column("created_by", sa.String(length=36), nullable=False),
        sa.Column("cover_media_id", sa.String(length=36), nullable=True),
        sa.Column("created_at", sa.DateTime(), nullable=False),
        sa.Column("updated_at", sa.DateTime(), nullable=False),
        sa.ForeignKeyConstraint(["created_by"], ["persons.id"], ondelete="CASCADE"),
        sa.PrimaryKeyConstraint("id"),
    )
    op.create_table(
        "album_media",
        sa.Column("id", sa.String(length=36), nullable=False),
        sa.Column("album_id", sa.String(length=36), nullable=False),
        sa.Column("media_id", sa.String(length=36), nullable=False),
        sa.Column("added_by", sa.String(length=36), nullable=False),
        sa.Column("created_at", sa.DateTime(), nullable=False),
        sa.ForeignKeyConstraint(["added_by"], ["persons.id"], ondelete="CASCADE"),
        sa.ForeignKeyConstraint(["album_id"], ["albums.id"], ondelete="CASCADE"),
        sa.ForeignKeyConstraint(["media_id"], ["media.id"], ondelete="CASCADE"),
        sa.PrimaryKeyConstraint("id"),
        sa.UniqueConstraint("album_id", "media_id", name="uq_album_media"),
    )
    op.create_table(
        "book_projects",
        sa.Column("id", sa.String(length=36), nullable=False),
        sa.Column("created_by", sa.String(length=36), nullable=False),
        sa.Column("title", sa.String(length=300), nullable=False),
        sa.Column("subtitle", sa.String(length=300), nullable=True),
        sa.Column("introduction", sa.Text(), nullable=True),
        sa.Column("person_ids", sa.Text(), nullable=True),
        sa.Column("story_ids", sa.Text(), nullable=True),
        sa.Column("media_ids", sa.Text(), nullable=True),
        sa.Column("include_timeline", sa.Boolean(), nullable=False),
        sa.Column("markdown_path", sa.String(length=500), nullable=True),
        sa.Column("pdf_path", sa.String(length=500), nullable=True),
        sa.Column("generated_at", sa.DateTime(), nullable=True),
        sa.Column("created_at", sa.DateTime(), nullable=False),
        sa.Column("updated_at", sa.DateTime(), nullable=False),
        sa.ForeignKeyConstraint(["created_by"], ["persons.id"], ondelete="CASCADE"),
        sa.PrimaryKeyConstraint("id"),
    )


def downgrade() -> None:
    op.drop_table("book_projects")
    op.drop_table("album_media")
    op.drop_table("albums")
    op.drop_table("prompt_campaign_recipients")
    op.drop_table("prompt_campaigns")
