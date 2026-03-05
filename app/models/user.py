from datetime import datetime
from sqlalchemy import DateTime
from sqlalchemy.orm import Mapped, mapped_column
from app.db.base import Base, TimestampMixin
from app.models.enums import UserRole


class User(Base, TimestampMixin):
    __tablename__ = "users"
    email: Mapped[str] = mapped_column(
        unique=True, 
        index=True
    )
    hashed_password: Mapped[str]
    role: Mapped[UserRole] = mapped_column(
        default="user"
    )
    email_verified: Mapped[bool] = mapped_column(
        default=False
    )
    is_locked: Mapped[bool] = mapped_column(
        default=False
    )
    failed_attempts: Mapped[int] = mapped_column(
        default=0
    )
    locked_until: Mapped[datetime | None] = mapped_column(
        DateTime(timezone=True),
        nullable=True
    )
    last_login: Mapped[datetime | None] = mapped_column(
        DateTime(timezone=True),
        nullable=True
    )