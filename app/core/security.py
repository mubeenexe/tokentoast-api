import hashlib
from passlib.context import CryptContext

from jose import jwt, JWTError
from datetime import datetime, timedelta, timezone

from app.core.config import settings

pwd_context = CryptContext(schemes=["bcrypt"], deprecated="auto")

def hash_password(password: str) -> str:
    return pwd_context.hash(password)

def verify_password(password: str, hashed: str) -> bool:
    return pwd_context.verify(password, hashed)

def hash_token(raw: str) -> str:
    return hashlib.sha256(raw.encode()).hexdigest()

def create_jwt_token(user_id: str, email: str, role: str) -> str:
    now = datetime.now(timezone.utc)
    expire = now + timedelta(seconds=settings.ACCESS_TOKEN_TTL)
    payload = {
        "sub": user_id,
        "email": email,
        "role": role,
        "type": "access",
        "iat": int(now.timestamp()),
        "exp": int(expire.timestamp())
    }
    token = jwt.encode(payload, settings.SECRET_KEY, algorithm=settings.ALGORITHM)
    return token

def verify_jwt_token(token: str) -> dict:
    try:
        payload = jwt.decode(token, settings.SECRET_KEY, algorithms=[settings.ALGORITHM])
    except JWTError:
        raise JWTError("Invalid or expired token")

    if payload.get("type") != "access":
        raise JWTError("Invalid token type")
    return payload
