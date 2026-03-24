import json

from sqlalchemy import String, Text
from sqlalchemy.orm import Mapped, mapped_column

from app.models.base import Base, TimestampMixin, generate_uuid
from app.services.theme_service import DEFAULT_THEME_SETTINGS, ThemeSettingsPayload


class AppThemeSettings(Base, TimestampMixin):
    __tablename__ = "app_theme_settings"

    id: Mapped[str] = mapped_column(String(36), primary_key=True, default=generate_uuid)
    singleton_key: Mapped[str] = mapped_column(String(32), unique=True, default="site")
    _settings_json: Mapped[str | None] = mapped_column("settings_json", Text, default="{}")

    @property
    def settings(self) -> dict[str, str]:
        stored = json.loads(self._settings_json) if self._settings_json else {}
        normalized = ThemeSettingsPayload.model_validate(
            {**DEFAULT_THEME_SETTINGS, **stored}
        )
        return normalized.model_dump()

    @settings.setter
    def settings(self, value: dict[str, str]) -> None:
        normalized = ThemeSettingsPayload.model_validate(
            {**DEFAULT_THEME_SETTINGS, **(value or {})}
        )
        self._settings_json = json.dumps(normalized.model_dump())
