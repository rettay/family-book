"""add external calendar sources and backfill legacy slash dates

Revision ID: d1f0c3b2a4e5
Revises: c27a00000001
Create Date: 2026-03-28 16:30:00.000000

"""

from typing import Sequence, Union

from alembic import op
import sqlalchemy as sa


revision: str = "d1f0c3b2a4e5"
down_revision: Union[str, Sequence[str], None] = "c27a00000001"
branch_labels: Union[str, Sequence[str], None] = None
depends_on: Union[str, Sequence[str], None] = None


def upgrade() -> None:
    op.create_table(
        "external_calendar_sources",
        sa.Column("id", sa.String(length=36), nullable=False),
        sa.Column("name", sa.String(length=200), nullable=False),
        sa.Column("url", sa.String(length=1000), nullable=False),
        sa.Column("source_type", sa.String(length=30), nullable=False, server_default="holiday"),
        sa.Column("enabled", sa.Boolean(), nullable=False, server_default=sa.true()),
        sa.Column("created_by", sa.String(length=36), nullable=True),
        sa.Column("created_at", sa.DateTime(), nullable=False),
        sa.Column("updated_at", sa.DateTime(), nullable=False),
        sa.PrimaryKeyConstraint("id"),
        sa.UniqueConstraint("url", name="uq_external_calendar_source_url"),
    )

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
                set_clause = ", ".join(f"{key} = :v_{key}" for key in updates)
                params = {f"v_{key}": value for key, value in updates.items()}
                params["pid"] = pid
                conn.execute(sa.text(f"UPDATE persons SET {set_clause} WHERE id = :pid"), params)


def downgrade() -> None:
    op.drop_table("external_calendar_sources")
