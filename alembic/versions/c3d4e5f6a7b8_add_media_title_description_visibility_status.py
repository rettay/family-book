"""add media title, description, visibility, and processing status fields

Revision ID: c3d4e5f6a7b8
Revises: b2c3d4e5f6a7
Create Date: 2026-03-30 12:00:00.000000
"""

from alembic import op
import sqlalchemy as sa


# revision identifiers, used by Alembic.
revision = "c3d4e5f6a7b8"
down_revision = "b2c3d4e5f6a7"
branch_labels = None
depends_on = None


def upgrade() -> None:
    with op.batch_alter_table("media") as batch_op:
        batch_op.add_column(sa.Column("title", sa.String(300), nullable=True))
        batch_op.add_column(sa.Column("description", sa.Text(), nullable=True))
        batch_op.add_column(sa.Column("visibility", sa.String(20), nullable=False, server_default="family"))
        batch_op.add_column(sa.Column("processing_status", sa.String(20), nullable=False, server_default="ready"))
        batch_op.drop_column("is_profile")

    # Copy existing caption values to description
    conn = op.get_bind()
    conn.execute(sa.text("UPDATE media SET description = caption WHERE caption IS NOT NULL AND caption != ''"))


def downgrade() -> None:
    with op.batch_alter_table("media") as batch_op:
        batch_op.add_column(sa.Column("is_profile", sa.Boolean(), nullable=True, server_default="0"))
        batch_op.drop_column("processing_status")
        batch_op.drop_column("visibility")
        batch_op.drop_column("description")
        batch_op.drop_column("title")
