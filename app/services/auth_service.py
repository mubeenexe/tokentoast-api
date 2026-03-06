import secrets
import uuid
from datetime import datetime, timedelta, timezone
from sqlalchemy.ext.asyncio import AsyncSession

from app.core.config import settings
from app.core.exceptions import AccountLockedError, EmailAlreadyExistsError, EmailNotVerifiedError, InvalidCredentialsError, InvalidTokenError
from app.core.security import create_jwt_token, hash_password, hash_token, verify_password, _get_dummy_hash
from app.models.enums import UserRole
from app.models.user import User
from app.repositories.token_repo import TokenRepository
from app.repositories.user_repo import UserRepository
from app.schemas.auth import LoginRequest, RegisterRequest


def _is_account_locked(user: User) -> bool:
    if not user.is_locked:
        return False
    if user.locked_until is None:
        return True
    locked_until = user.locked_until
    if locked_until.tzinfo is None:
        locked_until = locked_until.replace(tzinfo=timezone.utc)
    return datetime.now(timezone.utc) < locked_until


async def register(
    data: RegisterRequest,
    user_repo: UserRepository,
    db: AsyncSession
) -> User:
    existing_user = await user_repo.get_by_email(data.email)

    if existing_user:
        raise EmailAlreadyExistsError()

    hashed_password_str = hash_password(data.password)

    user = await user_repo.create(
        email=data.email,
        hashed_password=hashed_password_str,
        role=UserRole.USER,
        email_verified=False,
        is_locked=False,
        failed_attempts=0,
        locked_until=None,
        last_login=None,
    )

    await db.commit()
    return user


async def login(
    data: LoginRequest,
    user_agent: str,
    user_repo: UserRepository,
    token_repo: TokenRepository,
    db: AsyncSession
) -> tuple[str, str]:
    user = await user_repo.get_by_email(data.email)

    if not user:
        verify_password(data.password, _get_dummy_hash())
        raise InvalidCredentialsError()

    if _is_account_locked(user):
        raise AccountLockedError(user.locked_until)

    if not verify_password(data.password, user.hashed_password):
        await user_repo.increment_failed_attempts(user)
        raise InvalidCredentialsError()

    if not user.email_verified:
        raise EmailNotVerifiedError()

    await user_repo.reset_failed_attempts(user)

    access_token = create_jwt_token(str(user.id), user.email, user.role.value)

    raw_refresh_token = secrets.token_urlsafe(32)
    token_hash = hash_token(raw_refresh_token)
    family_id = uuid.uuid4()
    expires_at = datetime.now(timezone.utc) + timedelta(seconds=settings.REFRESH_TOKEN_TTL)

    await token_repo.create_token(
        user_id=user.id,
        token_hash=token_hash,
        family_id=family_id,
        expires_at=expires_at,
        user_agent=user_agent or None,
    )

    await db.commit()
    return access_token, raw_refresh_token

async def logout(raw_token: str, token_repo: TokenRepository, db: AsyncSession) -> None:
    token = await token_repo.get_by_hash(hash_token(raw_token))

    if not token: 
        raise InvalidTokenError("Invalid token")

    await token_repo.revoke_token(token)
    await db.commit()

async def refresh(raw_token: str, user_agent: str, token_repo: TokenRepository, user_repo: UserRepository, db: AsyncSession) -> tuple[str, str]:
    token = await token_repo.get_by_hash(hash_token(raw_token))

    if not token:
        raise InvalidTokenError("Invalid token")

    if token.is_revoked:
        await token_repo.revoke_family(token.family_id)
        raise InvalidTokenError("Token is revoked")

    if token.expires_at < datetime.now(timezone.utc):
        await token_repo.revoke_token(token)
        raise InvalidTokenError("Token has expired")

    # Revoke the current token
    await token_repo.revoke_token(token)

    # Fetch user only when we know we'll succeed
    user = await user_repo.get_by_id(token.user_id)

    # Issue new access token + new refresh token (same family_id)
    new_token = secrets.token_urlsafe(32)
    new_token_hash = hash_token(new_token)
    new_expires_at = datetime.now(timezone.utc) + timedelta(seconds=settings.REFRESH_TOKEN_TTL)

    await token_repo.create_token(
        user_id=token.user_id,
        token_hash=new_token_hash,
        family_id=token.family_id,
        expires_at=new_expires_at,
        user_agent=user_agent or None,
    )

    await db.commit()
    return create_jwt_token(str(user.id), user.email, user.role.value), new_token