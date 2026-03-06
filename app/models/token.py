import uuid
from datetime import datetime
from sqlalchemy import DateTime, ForeignKey, Text
from sqlalchemy.orm import Mapped, mapped_column
from app.db.base import Base, TimestampMixin

class RefreshToken(Base, TimestampMixin):
    __tablename__ = "refresh_tokens"

    user_id: Mapped[uuid.UUID] = mapped_column(
        ForeignKey("users.id"),
        nullable=False,
        index=True,
    )

    token_hash: Mapped[str] = mapped_column(
        unique=True,
        index=True,
        nullable=False,
    )

    family_id: Mapped[uuid.UUID] = mapped_column(
        index=True,
        nullable=False
    )

    is_revoked: Mapped[bool] = mapped_column(
        default=False,
        nullable=False,
    )

    expires_at: Mapped[datetime] = mapped_column(
        DateTime(timezone=True),
        nullable=False,
    )

    user_agent: Mapped[str | None] = mapped_column(
        Text,
        nullable=True
    )