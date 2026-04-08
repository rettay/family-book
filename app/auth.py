from fastapi import Depends, HTTPException, Request, status
from sqlalchemy.ext.asyncio import AsyncSession

from app.database import get_db
from app.models.person import Person
from app.roles import is_admin_actor
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
    current_user: Person | None = Depends(get_current_user),
) -> Person:
    if current_user is None:
        raise HTTPException(status_code=status.HTTP_401_UNAUTHORIZED, detail="Not authenticated")
    return current_user


async def require_admin(
    current_user: Person = Depends(require_auth),
) -> Person:
    if not is_admin_actor(current_user):
        raise HTTPException(status_code=status.HTTP_403_FORBIDDEN, detail="Admin required")
    return current_user
