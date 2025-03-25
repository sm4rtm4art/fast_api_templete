"""User models module."""

from datetime import datetime
from typing import Optional

from pydantic import BaseModel, EmailStr


class UserCreate(BaseModel):
    """User creation model."""

    username: str
    email: EmailStr
    password: str
    full_name: Optional[str] = None
    is_active: bool = True
    is_superuser: bool = False
    is_admin: bool = False
    disabled: bool = False

    class Config:
        """Pydantic config."""

        from_attributes = True


class UserResponse(BaseModel):
    """User response model."""

    id: int
    username: str
    email: str
    full_name: Optional[str] = None
    is_active: bool
    is_superuser: bool
    is_admin: bool
    disabled: bool
    created_at: datetime

    class Config:
        """Pydantic config."""

        from_attributes = True
