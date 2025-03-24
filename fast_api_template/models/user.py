"""User models module."""

from typing import Optional

from pydantic import BaseModel, EmailStr


class UserCreate(BaseModel):
    """User creation model."""

    username: str
    email: EmailStr
    password: str
    full_name: Optional[str] = None
    disabled: bool = False
    is_admin: bool = False
    is_active: bool = True
    is_superuser: bool = False
    # Alias for is_superuser for backward compatibility
    superuser: bool = False
