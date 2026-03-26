"""Health dashboard routes — API endpoint and HTML page for family health intelligence."""

import logging
import os

from fastapi import APIRouter, Depends, Request
from fastapi.responses import HTMLResponse
from fastapi.templating import Jinja2Templates
from sqlalchemy.ext.asyncio import AsyncSession

from app.auth import require_auth
from app.database import get_db
from app.i18n import translate
from app.models.person import Person
from app.services.health_dashboard_service import get_health_dashboard
from app.services.theme_service import get_runtime_theme_from_app

router = APIRouter(tags=["health_dashboard"])
logger = logging.getLogger(__name__)

_template_dir = os.path.join(os.path.dirname(os.path.dirname(__file__)), "templates")
templates = Jinja2Templates(directory=_template_dir)


def _ctx(request: Request, current_user: Person | None = None, **kwargs):
    locale = request.cookies.get("locale", "en")
    app_theme = get_runtime_theme_from_app(request.app)
    return {
        "request": request,
        "current_user": current_user,
        "locale": locale,
        "t": lambda key: translate(key, locale),
        "app_theme": app_theme,
        "brand_display_name": app_theme["brand_display_name"],
        "brand_tagline": app_theme["brand_tagline"],
        **kwargs,
    }


@router.get("/api/health-dashboard")
async def api_health_dashboard(
    current_user: Person = Depends(require_auth),
    db: AsyncSession = Depends(get_db),
):
    return await get_health_dashboard(db, current_user)


@router.get("/health-dashboard", response_class=HTMLResponse)
async def health_dashboard_page(
    request: Request,
    current_user: Person = Depends(require_auth),
    db: AsyncSession = Depends(get_db),
):
    dashboard = await get_health_dashboard(db, current_user)
    return templates.TemplateResponse("health_dashboard.html", _ctx(
        request,
        current_user,
        active_page="health",
        dashboard=dashboard,
    ))
