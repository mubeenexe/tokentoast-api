from datetime import datetime


class AuthError(Exception):
    """Base exception for authentication/authorization errors."""


class InvalidCredentialsError(AuthError):
    """Invalid email or password."""


class AccountLockedError(AuthError):
    """Account is locked due to too many failed attempts."""

    def __init__(self, locked_until: datetime | None, message: str = "Account is locked"):
        super().__init__(message)
        self.locked_until = locked_until


class EmailNotVerifiedError(AuthError):
    """User has not verified their email address."""


class EmailAlreadyExistsError(AuthError):
    """Email is already registered."""


class InvalidTokenError(AuthError):
    """Refresh token is invalid, not found, revoked, or expired."""