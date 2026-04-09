from fastapi import Depends, HTTPException, Request, status
from sqlalchemy.ext.asyncio import AsyncSession

from app.config import get_settings
from app.database import get_db
from app.models.person import Person
from app.roles import is_admin_actor
from app.services.hosted_archive_service import archive_member_access_allowed, get_hosted_archive
from app.services.auth_service import validate_session

SESSION_COOKIE_NAME = "session"


async def get_current_user(
    request: Request,
    db: AsyncSession = Depends(get_db),
) -> Person | None:
    token = request.cookies.get(SESSION_COOKIE_NAME)
    if not token:
        return None
    return await validate_session(db, token)


async def require_auth(
    request: Request,
    current_user: Person | None = Depends(get_current_user),
    db: AsyncSession = Depends(get_db),
) -> Person:
    if current_user is None:
        raise HTTPException(status_code=status.HTTP_401_UNAUTHORIZED, detail="Not authenticated")

    settings = get_settings()
    if settings.hosted_archive_enabled:
        archive = await get_hosted_archive(db)
        if archive is None:
            raise HTTPException(
                status_code=status.HTTP_503_SERVICE_UNAVAILABLE,
                detail="Hosted archive is not provisioned.",
            )
        allowed, denial_status, detail = archive_member_access_allowed(archive)
        if not allowed:
            admin_safe_path = is_admin_actor(current_user) and (
                request.url.path == "/settings"
                or request.url.path.startswith("/admin")
                or request.url.path.startswith("/api/admin")
                or request.url.path.startswith("/api/billing")
                or request.url.path == "/trust"
            )
            if not admin_safe_path:
                raise HTTPException(
                    status_code=denial_status or status.HTTP_403_FORBIDDEN,
                    detail=detail or "Archive access is unavailable.",
                )
    return current_user


async def require_admin(
    current_user: Person = Depends(require_auth),
) -> Person:
    if not is_admin_actor(current_user):
        raise HTTPException(status_code=status.HTTP_403_FORBIDDEN, detail="Admin required")
    return current_user
