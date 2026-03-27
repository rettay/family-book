"""add social profile fields and backfill dates

Revision ID: c27a00000001
Revises: b48cf4579cfc
Create Date: 2026-03-26 22:00:00.000000

"""
from typing import Sequence, Union

from alembic import op
import sqlalchemy as sa


# revision identifiers, used by Alembic.
revision: str = 'c27a00000001'
down_revision: Union[str, Sequence[str], None] = 'b48cf4579cfc'
branch_labels: Union[str, Sequence[str], None] = None
depends_on: Union[str, Sequence[str], None] = None


def upgrade() -> None:
    """Add social profile columns and backfill birth_date/death_date from raw."""
    # Social profile fields
    op.add_column('persons', sa.Column('social_instagram', sa.String(300), nullable=True))
    op.add_column('persons', sa.Column('social_facebook', sa.String(300), nullable=True))
    op.add_column('persons', sa.Column('social_twitter', sa.String(300), nullable=True))
    op.add_column('persons', sa.Column('social_linkedin', sa.String(300), nullable=True))
    op.add_column('persons', sa.Column('social_tiktok', sa.String(300), nullable=True))
    op.add_column('persons', sa.Column('social_youtube', sa.String(300), nullable=True))

    # Backfill: parse existing birth_date_raw → birth_date where ISO is null
    conn = op.get_bind()
    rows = conn.execute(
        sa.text(
            "SELECT id, birth_date_raw, death_date_raw "
            "FROM persons "
            "WHERE (birth_date IS NULL AND birth_date_raw IS NOT NULL AND birth_date_raw != '') "
            "   OR (death_date IS NULL AND death_date_raw IS NOT NULL AND death_date_raw != '')"
        )
    ).fetchall()

    if rows:
        from app.services.date_parsing import parse_date_raw_to_iso
        for row in rows:
            pid, birth_raw, death_raw = row[0], row[1], row[2]
            updates = {}
            if birth_raw:
                iso, prec = parse_date_raw_to_iso(birth_raw)
                if iso:
                    updates["birth_date"] = iso
                    updates["birth_date_precision"] = prec
            if death_raw:
                iso, prec = parse_date_raw_to_iso(death_raw)
                if iso:
                    updates["death_date"] = iso
                    updates["death_date_precision"] = prec
            if updates:
                set_clause = ", ".join(f"{k} = :v_{k}" for k in updates)
                params = {f"v_{k}": v for k, v in updates.items()}
                params["pid"] = pid
                conn.execute(
                    sa.text(f"UPDATE persons SET {set_clause} WHERE id = :pid"),
                    params,
                )


def downgrade() -> None:
    """Remove social profile columns."""
    op.drop_column('persons', 'social_youtube')
    op.drop_column('persons', 'social_tiktok')
    op.drop_column('persons', 'social_linkedin')
    op.drop_column('persons', 'social_twitter')
    op.drop_column('persons', 'social_facebook')
    op.drop_column('persons', 'social_instagram')
