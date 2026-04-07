"""add passkey credential and challenge tables

Revision ID: fb107_passkeys
Revises: a3c7f2e8b1d4
Create Date: 2026-04-07 00:00:00.000000

"""

from typing import Sequence, Union

from alembic import op
import sqlalchemy as sa


revision: str = "fb107_passkeys"
down_revision: Union[str, Sequence[str], None] = "a3c7f2e8b1d4"
branch_labels: Union[str, Sequence[str], None] = None
depends_on: Union[str, Sequence[str], None] = None


def upgrade() -> None:
    op.create_table(
        "passkey_credentials",
        sa.Column("id", sa.String(length=36), nullable=False),
        sa.Column("person_id", sa.String(length=36), nullable=False),
        sa.Column("credential_id", sa.String(length=500), nullable=False),
        sa.Column("public_key", sa.Text(), nullable=False),
        sa.Column("sign_count", sa.Integer(), nullable=False),
        sa.Column("label", sa.String(length=120), nullable=False),
        sa.Column("transports", sa.Text(), nullable=True),
        sa.Column("device_type", sa.String(length=40), nullable=True),
        sa.Column("backed_up", sa.Boolean(), nullable=False),
        sa.Column("created_at", sa.DateTime(), nullable=False),
        sa.Column("last_used_at", sa.DateTime(), nullable=True),
        sa.ForeignKeyConstraint(["person_id"], ["persons.id"], ondelete="CASCADE"),
        sa.PrimaryKeyConstraint("id"),
        sa.UniqueConstraint("credential_id"),
    )
    op.create_index(
        "idx_passkey_credentials_person_id",
        "passkey_credentials",
        ["person_id"],
        unique=False,
    )
    op.create_index(
        "idx_passkey_credentials_credential_id",
        "passkey_credentials",
        ["credential_id"],
        unique=False,
    )

    op.create_table(
        "passkey_challenges",
        sa.Column("id", sa.String(length=36), nullable=False),
        sa.Column("person_id", sa.String(length=36), nullable=True),
        sa.Column("challenge", sa.String(length=200), nullable=False),
        sa.Column("ceremony", sa.String(length=20), nullable=False),
        sa.Column("expires_at", sa.DateTime(), nullable=False),
        sa.Column("used_at", sa.DateTime(), nullable=True),
        sa.Column("created_at", sa.DateTime(), nullable=False),
        sa.ForeignKeyConstraint(["person_id"], ["persons.id"], ondelete="CASCADE"),
        sa.PrimaryKeyConstraint("id"),
    )
    op.create_index(
        "idx_passkey_challenges_person_id",
        "passkey_challenges",
        ["person_id"],
        unique=False,
    )
    op.create_index(
        "idx_passkey_challenges_ceremony",
        "passkey_challenges",
        ["ceremony"],
        unique=False,
    )


def downgrade() -> None:
    op.drop_index("idx_passkey_challenges_ceremony", table_name="passkey_challenges")
    op.drop_index("idx_passkey_challenges_person_id", table_name="passkey_challenges")
    op.drop_table("passkey_challenges")
    op.drop_index("idx_passkey_credentials_credential_id", table_name="passkey_credentials")
    op.drop_index("idx_passkey_credentials_person_id", table_name="passkey_credentials")
    op.drop_table("passkey_credentials")
