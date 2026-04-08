"""add person privacy and role columns

Revision ID: c4f8e2a1b6d9
Revises: fb107_passkeys
Create Date: 2026-04-08 00:00:00.000000
"""

from typing import Sequence, Union

from alembic import op
import sqlalchemy as sa


revision: str = "c4f8e2a1b6d9"
down_revision: Union[str, Sequence[str], None] = "fb107_passkeys"
branch_labels: Union[str, Sequence[str], None] = None
depends_on: Union[str, Sequence[str], None] = None


def upgrade() -> None:
    with op.batch_alter_table("persons") as batch_op:
        batch_op.add_column(
            sa.Column(
                "role",
                sa.String(length=20),
                nullable=False,
                server_default="member",
            )
        )
        batch_op.add_column(
            sa.Column(
                "contact_visibility",
                sa.String(length=20),
                nullable=False,
                server_default="close_family",
            )
        )
        batch_op.add_column(
            sa.Column(
                "sensitive_visibility",
                sa.String(length=20),
                nullable=False,
                server_default="staff",
            )
        )

    op.execute("UPDATE persons SET role = 'admin' WHERE is_admin = 1")
    op.execute("UPDATE persons SET role = 'member' WHERE role IS NULL OR role = ''")
    op.execute(
        "UPDATE persons SET contact_visibility = 'close_family' "
        "WHERE contact_visibility IS NULL OR contact_visibility = ''"
    )
    op.execute(
        "UPDATE persons SET sensitive_visibility = 'staff' "
        "WHERE sensitive_visibility IS NULL OR sensitive_visibility = ''"
    )

    with op.batch_alter_table("persons") as batch_op:
        batch_op.alter_column("role", server_default=None)
        batch_op.alter_column("contact_visibility", server_default=None)
        batch_op.alter_column("sensitive_visibility", server_default=None)


def downgrade() -> None:
    with op.batch_alter_table("persons") as batch_op:
        batch_op.drop_column("sensitive_visibility")
        batch_op.drop_column("contact_visibility")
        batch_op.drop_column("role")
