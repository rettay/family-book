import json

from sqlalchemy import ForeignKey, String, Text
from sqlalchemy.orm import Mapped, mapped_column

from app.models.base import Base, TimestampMixin, generate_uuid


DEFAULT_TREE_PREFERENCES = {
    "show_names": True,
    "show_nicknames": False,
    "show_birth_dates": False,
    "show_country_flags": True,
    "show_photos": True,
    "show_occupation": False,
}


class TreePreference(Base, TimestampMixin):
    __tablename__ = "tree_preferences"

    id: Mapped[str] = mapped_column(String(36), primary_key=True, default=generate_uuid)
    person_id: Mapped[str] = mapped_column(
        String(36), ForeignKey("persons.id", ondelete="CASCADE"), unique=True
    )
    _display_options: Mapped[str | None] = mapped_column("display_options", Text, default="{}")

    @property
    def display_options(self) -> dict[str, bool]:
        stored = json.loads(self._display_options) if self._display_options else {}
        return {**DEFAULT_TREE_PREFERENCES, **stored}

    @display_options.setter
    def display_options(self, value: dict[str, bool]) -> None:
        normalized = {
            key: bool(value.get(key, default))
            for key, default in DEFAULT_TREE_PREFERENCES.items()
        }
        self._display_options = json.dumps(normalized)
