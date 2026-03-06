import uuid
from pydantic import BaseModel, ConfigDict, field_validator

from app.models.enums import UserRole

class RegisterRequest(BaseModel):
    email: str
    password: str

    @field_validator("password")
    def validate_password(cls, v: str) -> str:
        import re
        errors = []
        if len(v) < 8:
            errors.append("at least 8 characters")
        if not re.search(r'[A-Z]', v):
            errors.append("at least one uppercase letter")
        if not re.search(r'\d', v):
            errors.append("at least one digit")
        if not re.search(r'[\W_]', v):
            errors.append("at least one special character")
        if errors:
            raise ValueError(
                f"Password must contain {', '.join(errors)}."
            )
        return v

    @field_validator("email")
    def normalize_email(cls, v: str) -> str:
        return v.lower()

class LoginRequest(BaseModel):
    email: str
    password: str

    @field_validator("email")
    def normalize_email(cls, v: str) -> str:
        return v.lower()


class UserOut(BaseModel):
    id: uuid.UUID
    email: str
    role: UserRole
    email_verified: bool

    model_config = ConfigDict(from_attributes=True)

class MessageResponse(BaseModel):
    message: str