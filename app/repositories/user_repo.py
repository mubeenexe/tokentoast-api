from datetime import datetime, timedelta, timezone

from sqlalchemy import select
from app.core.config import settings
from app.repositories.base import BaseRepository
from app.models.user import User

class UserRepository(BaseRepository[User]):
    async def get_by_email(self, email: str) -> User | None:
        result = await self.db.execute(select(User).where(User.email == email))
        return result.scalars().first()
    
    async def increment_failed_attempts(self, user: User) -> User:
        user.failed_attempts += 1
        if user.failed_attempts >= settings.LOCK_THRESHOLD:
            until = datetime.now(timezone.utc) + timedelta(minutes=settings.LOCKOUT_DURATION_MIN)
            await self.lock_account(user, until)
        else:
            await self.save(user)
        return user

    async def reset_failed_attempts(self, user: User) -> User:
        user.failed_attempts = 0
        user.is_locked = False
        user.locked_until = None
        await self.save(user)
        return user

    async def lock_account(self, user: User, until: datetime) -> User:
        user.is_locked = True
        user.locked_until = until
        await self.save(user)
        return user