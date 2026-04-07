"""PersonOccupation model — SCD Type 2 occupation history."""

from sqlalchemy import ForeignKey, Index, String, Text
from sqlalchemy.orm import Mapped, mapped_column

from app.models.base import Base, TimestampMixin, generate_uuid


class PersonOccupation(Base, TimestampMixin):
    __tablename__ = "person_occupations"

    id: Mapped[str] = mapped_column(String(36), primary_key=True, default=generate_uuid)
    person_id: Mapped[str] = mapped_column(
        String(36), ForeignKey("persons.id", ondelete="CASCADE"), nullable=False
    )
    title: Mapped[str] = mapped_column(Text, nullable=False)
    employer: Mapped[str | None] = mapped_column(Text, nullable=True, default=None)
    # Free text — accepts "1985", "circa 1920", "early 1960s", etc. No parsing.
    start_date: Mapped[str | None] = mapped_column(String(100), nullable=True, default=None)
    # Null means currently in this role.
    end_date: Mapped[str | None] = mapped_column(String(100), nullable=True, default=None)
    # Who added this record — used for delete authorization (adder or admin).
    added_by_person_id: Mapped[str | None] = mapped_column(
        String(36), ForeignKey("persons.id", ondelete="SET NULL"), nullable=True, default=None
    )
    source: Mapped[str | None] = mapped_column(Text, nullable=True, default=None)

    __table_args__ = (Index("ix_person_occupations_person_id", "person_id"),)

    def __repr__(self) -> str:
        return f"<PersonOccupation {self.id[:8]} person={self.person_id[:8]} title={self.title!r}>"
