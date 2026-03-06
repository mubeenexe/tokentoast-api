import uuid
from fastapi import Cookie, Depends, HTTPException
from sqlalchemy import select
from sqlalchemy.ext.asyncio import AsyncSession

from app.db.session import get_db
from app.models.enums import UserRole
from app.models.user import User
from app.core.security import verify_jwt_token

async def get_current_user(
    access_token: str | None = Cookie(None),
    db: AsyncSession = Depends(get_db)
) -> User:
    if not access_token:
        raise HTTPException(status_code=401, detail="Unauthorized")

    try:
        payload = verify_jwt_token(access_token)
    except Exception:
        raise HTTPException(status_code=401, detail="Unauthorized")

    user_id = payload.get("sub")
    if not user_id:
        raise HTTPException(status_code=401, detail="Unauthorized")
    try:
        user_uuid = uuid.UUID(user_id)
    except Exception:
        raise HTTPException(status_code=401, detail="Unauthorized")

    result = await db.execute(select(User).where(User.id == user_uuid))
    user = result.scalar_one_or_none()
    if not user:
        raise HTTPException(status_code=401, detail="Unauthorized")

    if user.is_locked:
        raise HTTPException(status_code=423, detail="Account is locked")

    return user

def require_role(*roles: UserRole):
    async def dependency(current_user: User = Depends(get_current_user)) -> User:
        if current_user.role not in roles:
            raise HTTPException(status_code=403, detail="Forbidden")
        return current_user
    return dependency