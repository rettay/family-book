"""add_person_slug

Revision ID: b919e1b33636
Revises: 9e0aa75cb010
Create Date: 2026-03-26 14:43:46.573504

"""
from typing import Sequence, Union

from alembic import op
import re
import unicodedata
import sqlalchemy as sa


# revision identifiers, used by Alembic.
revision: str = 'b919e1b33636'
down_revision: Union[str, Sequence[str], None] = '9e0aa75cb010'
branch_labels: Union[str, Sequence[str], None] = None
depends_on: Union[str, Sequence[str], None] = None


def _slugify(text: str) -> str:
    text = unicodedata.normalize("NFKD", text).encode("ascii", "ignore").decode("ascii")
    text = re.sub(r"[^\w\s-]", "", text.lower())
    return re.sub(r"[-\s]+", "-", text).strip("-")


def _generate_slug(first_name, last_name, person_id):
    short_id = person_id[:8]
    parts = []
    if first_name:
        parts.append(_slugify(first_name))
    if last_name:
        parts.append(_slugify(last_name))
    parts.append(short_id)
    return "-".join(p for p in parts if p)


def upgrade() -> None:
    """Upgrade schema."""
    with op.batch_alter_table('persons', schema=None) as batch_op:
        batch_op.add_column(sa.Column('slug', sa.String(length=200), nullable=True))
        batch_op.create_index(batch_op.f('ix_persons_slug'), ['slug'], unique=True)

    # Backfill slugs for existing persons
    conn = op.get_bind()
    rows = conn.execute(sa.text("SELECT id, first_name, last_name FROM persons")).fetchall()
    for row in rows:
        slug = _generate_slug(row[1], row[2], row[0])
        conn.execute(
            sa.text("UPDATE persons SET slug = :slug WHERE id = :id"),
            {"slug": slug, "id": row[0]},
        )


def downgrade() -> None:
    """Downgrade schema."""
    with op.batch_alter_table('persons', schema=None) as batch_op:
        batch_op.drop_index(batch_op.f('ix_persons_slug'))
        batch_op.drop_column('slug')
