"""User models module."""

from collections.abc import Callable, Generator
from datetime import UTC, datetime
from typing import Any

from pydantic import BaseModel
from sqlmodel import Field, Session, SQLModel

from ..utils.password import get_password_hash


class HashedPassword(str):
    """Takes a plain text password and hashes it.

    use this as a field in your SQLModel

    class User(SQLModel, table=True):
        username: str
        password: HashedPassword
    """

    @classmethod
    def __get_validators__(cls) -> Generator[Callable[[Any], str], None, None]:
        yield cls.validate

    @classmethod
    def validate(cls, v: Any) -> str:
        if not isinstance(v, str):
            raise TypeError("string required")

        if "password" in v:
            return cls(get_password_hash(v))

        return cls(v)


# mypy: disable-error-code="call-arg"
class User(SQLModel, table=True):
    """User model."""

    __tablename__ = "user"

    id: int | None = Field(default=None, primary_key=True)
    username: str = Field(unique=True, index=True)
    email: str
    hashed_password: str
    full_name: str | None = None
    is_active: bool = Field(default=True)
    is_superuser: bool = Field(default=False)
    is_admin: bool = Field(default=False)
    disabled: bool = Field(default=False)
    created_at: datetime = Field(default_factory=lambda: datetime.now(UTC))

    @classmethod
    def create(cls, user_in: "UserCreate", session: Session) -> "User":
        """Create a new user."""
        hashed_password = get_password_hash(user_in.password)
        db_user = cls(
            username=user_in.username,
            email=user_in.email,
            hashed_password=hashed_password,
            full_name=user_in.full_name,
            is_active=user_in.is_active,
            is_superuser=user_in.is_superuser,
            is_admin=user_in.is_admin,
            disabled=user_in.disabled,
        )
        session.add(db_user)
        session.commit()
        session.refresh(db_user)
        return db_user

    def to_response(self) -> "UserResponse":
        """Convert to response model."""
        return UserResponse(
            id=self.id if self.id is not None else 0,
            username=self.username,
            email=self.email,
            full_name=self.full_name,
            is_active=self.is_active,
            is_superuser=self.is_superuser,
            is_admin=self.is_admin,
            disabled=self.disabled,
            created_at=self.created_at,
        )


class UserCreate(BaseModel):
    """User creation model."""

    username: str
    email: str
    password: str
    full_name: str | None = None
    is_active: bool = True
    is_superuser: bool = False
    is_admin: bool = False
    disabled: bool = False


class UserResponse(BaseModel):
    """User response model."""

    id: int
    username: str
    email: str
    full_name: str | None = None
    is_active: bool = True
    is_superuser: bool = False
    is_admin: bool = False
    disabled: bool = False
    created_at: datetime


class UserPasswordPatch(BaseModel):
    """Model for password change operations."""

    password: str
    password_confirm: str
