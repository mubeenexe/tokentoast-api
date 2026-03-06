from datetime import datetime
import uuid

from sqlalchemy import select, update
from app.repositories.base import BaseRepository
from app.models.token import RefreshToken

class TokenRepository(BaseRepository[RefreshToken]):
    async def create_token(self, user_id: uuid.UUID, token_hash: str, family_id: uuid.UUID, expires_at: datetime, user_agent: str | None)-> RefreshToken:
        refresh_token = RefreshToken(
            user_id=user_id,
            token_hash=token_hash,
            family_id=family_id,
            expires_at=expires_at,
            user_agent=user_agent,
            is_revoked=False,
        )
        await self.save(refresh_token)
        return refresh_token

    async def get_by_hash(self,token_hash: str) -> RefreshToken | None:
        result = await self.db.execute(select(RefreshToken).where(RefreshToken.token_hash == token_hash))
        return result.scalars().first()

    async def revoke_token(self, token: RefreshToken) -> None:
        token.is_revoked = True
        await self.save(token)
        
    async def revoke_family(self, family_id: uuid.UUID) -> None:
        await self.db.execute(update(RefreshToken).where(RefreshToken.family_id == family_id).values(is_revoked=True))

    async def revoke_all_for_user(self, user_id: uuid.UUID) -> None:
        await self.db.execute(update(RefreshToken).where(RefreshToken.user_id == user_id).values(is_revoked=True))