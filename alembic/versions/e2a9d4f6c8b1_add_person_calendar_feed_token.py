"""add person calendar feed token

Revision ID: e2a9d4f6c8b1
Revises: d1f0c3b2a4e5
Create Date: 2026-03-28 17:10:00.000000

"""

from typing import Sequence, Union
import uuid

from alembic import op
import sqlalchemy as sa


revision: str = "e2a9d4f6c8b1"
down_revision: Union[str, Sequence[str], None] = "d1f0c3b2a4e5"
branch_labels: Union[str, Sequence[str], None] = None
depends_on: Union[str, Sequence[str], None] = None


def upgrade() -> None:
    op.add_column("persons", sa.Column("calendar_feed_token", sa.String(length=36), nullable=True))
    conn = op.get_bind()
    rows = conn.execute(sa.text("SELECT id FROM persons WHERE calendar_feed_token IS NULL")).fetchall()
    for row in rows:
        conn.execute(
            sa.text("UPDATE persons SET calendar_feed_token = :token WHERE id = :pid"),
            {"pid": row[0], "token": str(uuid.uuid4())},
        )
    with op.batch_alter_table("persons", recreate="always") as batch_op:
        batch_op.alter_column("calendar_feed_token", existing_type=sa.String(length=36), nullable=False)
        batch_op.create_unique_constraint("uq_persons_calendar_feed_token", ["calendar_feed_token"])


def downgrade() -> None:
    with op.batch_alter_table("persons", recreate="always") as batch_op:
        batch_op.drop_constraint("uq_persons_calendar_feed_token", type_="unique")
        batch_op.drop_column("calendar_feed_token")
