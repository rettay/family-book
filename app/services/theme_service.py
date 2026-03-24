from __future__ import annotations

import re
from typing import Any

from pydantic import BaseModel, ConfigDict, field_validator
from sqlalchemy import select
from sqlalchemy.ext.asyncio import AsyncSession

HEX_COLOR_RE = re.compile(r"^#[0-9a-fA-F]{6}$")

DEFAULT_THEME_SETTINGS = {
    "brand_display_name": "Family Book",
    "brand_tagline": "Private family tree and archive",
    "background_color": "#faf8f5",
    "surface_color": "#fefcf9",
    "primary_color": "#2d5016",
    "accent_color": "#c49a3c",
    "text_color": "#2c2c2c",
    "muted_text_color": "#6b6054",
    "border_color": "#e0d6c8",
    "theme_color": "#faf8f5",
}

DEFAULT_MANIFEST_DESCRIPTION = "Private family tree and archive"
SITE_THEME_SINGLETON_KEY = "site"


class ThemeSettingsPayload(BaseModel):
    model_config = ConfigDict(str_strip_whitespace=True)

    brand_display_name: str = DEFAULT_THEME_SETTINGS["brand_display_name"]
    brand_tagline: str = DEFAULT_THEME_SETTINGS["brand_tagline"]
    background_color: str = DEFAULT_THEME_SETTINGS["background_color"]
    surface_color: str = DEFAULT_THEME_SETTINGS["surface_color"]
    primary_color: str = DEFAULT_THEME_SETTINGS["primary_color"]
    accent_color: str = DEFAULT_THEME_SETTINGS["accent_color"]
    text_color: str = DEFAULT_THEME_SETTINGS["text_color"]
    muted_text_color: str = DEFAULT_THEME_SETTINGS["muted_text_color"]
    border_color: str = DEFAULT_THEME_SETTINGS["border_color"]
    theme_color: str = DEFAULT_THEME_SETTINGS["theme_color"]

    @field_validator(
        "background_color",
        "surface_color",
        "primary_color",
        "accent_color",
        "text_color",
        "muted_text_color",
        "border_color",
        "theme_color",
        mode="before",
    )
    @classmethod
    def _normalize_color(cls, value: Any) -> str:
        if not isinstance(value, str):
            raise ValueError("Theme colors must be hex strings")
        normalized = value.strip().lower()
        if not HEX_COLOR_RE.match(normalized):
            raise ValueError("Theme colors must use #rrggbb format")
        return normalized

    @field_validator("brand_display_name")
    @classmethod
    def _validate_brand_display_name(cls, value: str) -> str:
        if len(value) < 2:
            raise ValueError("Brand display name is too short")
        if len(value) > 80:
            raise ValueError("Brand display name is too long")
        return value

    @field_validator("brand_tagline")
    @classmethod
    def _validate_brand_tagline(cls, value: str) -> str:
        if len(value) > 160:
            raise ValueError("Brand tagline is too long")
        return value


def _hex_to_rgb_tuple(value: str) -> tuple[int, int, int]:
    value = value.lstrip("#")
    return tuple(int(value[idx : idx + 2], 16) for idx in (0, 2, 4))


def _rgb_tuple_to_hex(rgb: tuple[int, int, int]) -> str:
    return "#{:02x}{:02x}{:02x}".format(*rgb)


def _blend(color_a: str, color_b: str, ratio: float) -> str:
    ratio = max(0.0, min(1.0, ratio))
    a = _hex_to_rgb_tuple(color_a)
    b = _hex_to_rgb_tuple(color_b)
    return _rgb_tuple_to_hex(
        tuple(round(a[idx] * (1.0 - ratio) + b[idx] * ratio) for idx in range(3))
    )


def _darken(color: str, amount: float) -> str:
    return _blend(color, "#000000", amount)


def _lighten(color: str, amount: float) -> str:
    return _blend(color, "#ffffff", amount)


def _rgb_string(value: str) -> str:
    return ", ".join(str(component) for component in _hex_to_rgb_tuple(value))


def _build_css_variables(settings: dict[str, str]) -> dict[str, str]:
    background = settings["background_color"]
    surface = settings["surface_color"]
    primary = settings["primary_color"]
    accent = settings["accent_color"]
    text = settings["text_color"]
    muted = settings["muted_text_color"]
    border = settings["border_color"]

    return {
        "--bg": background,
        "--bg-rgb": _rgb_string(background),
        "--bg-warm": _blend(background, surface, 0.45),
        "--cream": _lighten(background, 0.1),
        "--cream-dark": _blend(background, border, 0.45),
        "--warm-white": surface,
        "--surface-rgb": _rgb_string(surface),
        "--green-deep": primary,
        "--green-mid": _darken(primary, 0.12),
        "--green-light": _lighten(primary, 0.35),
        "--green-pale": _lighten(primary, 0.86),
        "--amber": accent,
        "--amber-light": _lighten(accent, 0.62),
        "--amber-pale": _lighten(accent, 0.88),
        "--brown-dark": _darken(text, 0.08),
        "--brown-mid": _blend(text, muted, 0.45),
        "--brown-light": _lighten(muted, 0.3),
        "--warm-gray": muted,
        "--text": text,
        "--text-muted": muted,
        "--text-light": _lighten(muted, 0.22),
        "--border": border,
        "--border-light": _lighten(border, 0.35),
        "--success": primary,
        "--success-light": _lighten(primary, 0.86),
        "--primary-rgb": _rgb_string(primary),
    }


def build_runtime_theme(settings: dict[str, str] | None = None) -> dict[str, Any]:
    normalized = ThemeSettingsPayload.model_validate(
        {**DEFAULT_THEME_SETTINGS, **(settings or {})}
    ).model_dump()
    brand_display_name = normalized["brand_display_name"]
    tagline = normalized["brand_tagline"]
    return {
        "settings": normalized,
        "brand_display_name": brand_display_name,
        "brand_tagline": tagline,
        "theme_color": normalized["theme_color"],
        "css_variables": _build_css_variables(normalized),
        "manifest": {
            "name": brand_display_name,
            "short_name": brand_display_name[:12] or brand_display_name,
            "description": tagline or DEFAULT_MANIFEST_DESCRIPTION,
            "start_url": "/",
            "display": "standalone",
            "background_color": normalized["background_color"],
            "theme_color": normalized["theme_color"],
            "orientation": "any",
            "icons": [
                {
                    "src": "/static/icons/icon-192.png",
                    "sizes": "192x192",
                    "type": "image/png",
                    "purpose": "any maskable",
                },
                {
                    "src": "/static/icons/icon-512.png",
                    "sizes": "512x512",
                    "type": "image/png",
                    "purpose": "any maskable",
                },
            ],
            "share_target": {
                "action": "/api/share",
                "method": "POST",
                "enctype": "multipart/form-data",
                "params": {
                    "title": "title",
                    "text": "text",
                    "files": [{"name": "media", "accept": ["image/*", "video/*"]}],
                },
            },
            "categories": ["lifestyle", "social"],
            "lang": "en",
            "dir": "ltr",
        },
    }


def get_runtime_theme_from_app(app) -> dict[str, Any]:
    return getattr(app.state, "site_theme", build_runtime_theme())


async def get_or_create_theme_settings_record(db: AsyncSession):
    from app.models.settings import AppThemeSettings

    result = await db.execute(
        select(AppThemeSettings).where(
            AppThemeSettings.singleton_key == SITE_THEME_SINGLETON_KEY
        )
    )
    settings = result.scalar_one_or_none()
    if settings is None:
        settings = AppThemeSettings(singleton_key=SITE_THEME_SINGLETON_KEY)
        settings.settings = DEFAULT_THEME_SETTINGS
        db.add(settings)
        await db.flush()
    return settings


async def load_runtime_theme(db: AsyncSession) -> dict[str, Any]:
    settings = await get_or_create_theme_settings_record(db)
    return build_runtime_theme(settings.settings)


async def sync_runtime_theme(app, db: AsyncSession) -> dict[str, Any]:
    runtime_theme = await load_runtime_theme(db)
    app.state.site_theme = runtime_theme
    return runtime_theme
