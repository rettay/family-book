"""add multi-value contact, social, name history, and obituary url fields

Revision ID: b2c3d4e5f6a7
Revises: a1b2c3d4e5f6
Create Date: 2026-03-29 18:00:00.000000
"""

from alembic import op
import sqlalchemy as sa


# revision identifiers, used by Alembic.
revision = "b2c3d4e5f6a7"
down_revision = "a1b2c3d4e5f6"
branch_labels = None
depends_on = None


def upgrade() -> None:
    with op.batch_alter_table("persons") as batch_op:
        batch_op.add_column(sa.Column("obituary_url", sa.String(1000), nullable=True))
        batch_op.add_column(sa.Column("contact_phones", sa.Text(), nullable=True, server_default="[]"))
        batch_op.add_column(sa.Column("contact_emails", sa.Text(), nullable=True, server_default="[]"))
        batch_op.add_column(sa.Column("social_accounts", sa.Text(), nullable=True, server_default="[]"))
        batch_op.add_column(sa.Column("name_history", sa.Text(), nullable=True, server_default="[]"))

    # Data migration: consolidate existing single-field contact data into new arrays
    conn = op.get_bind()

    # Migrate contact_phone → contact_phones
    # Note: contact_phone is EncryptedText so we copy the encrypted value as-is
    # into a JSON array wrapper. Since both old and new columns use EncryptedText,
    # and the encryption/decryption happens at the ORM layer, we cannot safely
    # re-encrypt here. The old columns are preserved for backward compatibility.
    # The ORM-level data consolidation will happen on first edit of each person.

    # Migrate social_* → social_accounts
    # Same constraint: social_* columns are plain text, but we'd need to build
    # JSON arrays. We do this for unencrypted social fields since they're plain strings.
    rows = conn.execute(
        sa.text(
            "SELECT id, social_instagram, social_facebook, social_twitter, "
            "social_linkedin, social_tiktok, social_youtube FROM persons"
        )
    ).fetchall()

    for row in rows:
        accounts = []
        platform_map = [
            ("instagram", row[1]),
            ("facebook", row[2]),
            ("twitter", row[3]),
            ("linkedin", row[4]),
            ("tiktok", row[5]),
            ("youtube", row[6]),
        ]
        for platform, value in platform_map:
            if value and value.strip():
                accounts.append({"platform": platform, "url": value.strip(), "is_visible": True})
        if accounts:
            import json
            conn.execute(
                sa.text("UPDATE persons SET social_accounts = :val WHERE id = :pid"),
                {"val": json.dumps(accounts), "pid": row[0]},
            )


def downgrade() -> None:
    with op.batch_alter_table("persons") as batch_op:
        batch_op.drop_column("name_history")
        batch_op.drop_column("social_accounts")
        batch_op.drop_column("contact_emails")
        batch_op.drop_column("contact_phones")
        batch_op.drop_column("obituary_url")
