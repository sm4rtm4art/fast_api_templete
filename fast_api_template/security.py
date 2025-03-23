from collections.abc import Callable, Generator
from datetime import datetime, timedelta
from typing import Any, cast

from fastapi import Depends, HTTPException, status
from fastapi.security import OAuth2PasswordBearer
from jose import JWTError, jwt
from passlib.context import CryptContext
from pydantic import BaseModel
from sqlmodel import Field, Relationship, SQLModel, Session, select

from fast_api_template.models.content import Content

from .config import settings
from .db import engine

pwd_context = CryptContext(schemes=["bcrypt"], deprecated="auto")
oauth2_scheme = OAuth2PasswordBearer(tokenUrl="token")

SECRET_KEY = settings.security.secret_key
ALGORITHM = settings.security.algorithm


class Token(BaseModel):
    access_token: str
    refresh_token: str
    token_type: str


class RefreshToken(BaseModel):
    refresh_token: str


class TokenData(BaseModel):
    username: str | None = None


class HashedPassword(str):
    """Takes a plain text password and hashes it.

    use this as a field in your SQLModel

    class User(SQLModel, table=True):
        username: str
        password: HashedPassword

    """

    @classmethod
    def __get_validators__(cls) -> Generator[Callable[[Any], str], None, None]:
        # one or more validators may be yielded which will be called in the
        # order to validate the input, each validator will receive as an input
        # the value returned from the previous validator
        yield cls.validate

    @classmethod
    def validate(cls, v: Any) -> str:
        if not isinstance(v, str):
            raise TypeError("string required")

        if "password" in v:
            # original needed from_attributes=True, but I dropped that because
            # we need this to work for both Pydantic v1 and v2
            return cls(get_password_hash(v))

        # assume the value is already hashed
        return cls(v)


# Define the User table
class User(SQLModel, table=True):  # type: ignore
    """User model for authentication."""

    id: int | None = Field(default=None, primary_key=True)
    username: str = Field(unique=True)
    email: str | None = Field(default=None)
    full_name: str | None = Field(default=None)
    disabled: bool | None = Field(default=False)
    hashed_password: str
    created_at: datetime = Field(default_factory=datetime.utcnow)

    # Relationships
    contents: list["Content"] = Relationship(back_populates="user")


class UserCreate(BaseModel):
    username: str
    email: str | None = None
    full_name: str | None = None
    password: str


class UserResponse(BaseModel):
    id: int
    username: str
    email: str | None = None
    full_name: str | None = None
    disabled: bool | None = None
    created_at: datetime


class UserPasswordPatch(BaseModel):
    """Model for password change operations."""

    password: str
    password_confirm: str


def verify_password(plain_password: str, hashed_password: str) -> bool:
    return pwd_context.verify(plain_password, hashed_password)


def get_password_hash(password: str) -> str:
    return pwd_context.hash(password)


def authenticate_user(username: str, password: str) -> User | bool:
    """Authenticate a user"""
    with Session(engine) as session:
        statement = select(User).where(User.username == username)
        user = session.exec(statement).first()
        if not user:
            return False
        if not verify_password(password, user.hashed_password):
            return False
        return user


def create_access_token(data: dict[str, Any], expires_delta: timedelta | None = None) -> str:
    to_encode = data.copy()
    if expires_delta:
        expire = datetime.utcnow() + expires_delta
    else:
        expire = datetime.utcnow() + timedelta(minutes=15)
    to_encode.update({"exp": expire})
    encoded_jwt = jwt.encode(to_encode, SECRET_KEY, algorithm=ALGORITHM)
    return encoded_jwt


def create_refresh_token(data: dict[str, Any], expires_delta: timedelta | None = None) -> str:
    to_encode = data.copy()
    if expires_delta:
        expire = datetime.utcnow() + expires_delta
    else:
        expire = datetime.utcnow() + timedelta(days=7)
    to_encode.update({"exp": expire})
    encoded_jwt = jwt.encode(to_encode, SECRET_KEY, algorithm=ALGORITHM)
    return encoded_jwt


def decode_token(token: str) -> dict[str, Any]:
    """Decode a JWT token."""
    credentials_exception = HTTPException(
        status_code=status.HTTP_401_UNAUTHORIZED,
        detail="Could not validate credentials",
        headers={"WWW-Authenticate": "Bearer"},
    )

    try:
        payload = jwt.decode(token, SECRET_KEY, algorithms=[ALGORITHM])
        username: str = cast(str, payload.get("sub", ""))
        if username == "":
            raise credentials_exception
        token_data = TokenData(username=username)
    except JWTError:
        raise credentials_exception

    return payload


def get_current_user(token: str = Depends(oauth2_scheme)) -> User:
    credentials_exception = HTTPException(
        status_code=status.HTTP_401_UNAUTHORIZED,
        detail="Could not validate credentials",
        headers={"WWW-Authenticate": "Bearer"},
    )

    try:
        payload = jwt.decode(token, SECRET_KEY, algorithms=[ALGORITHM])
        username: str = cast(str, payload.get("sub", ""))
        if username == "":
            raise credentials_exception
        token_data = TokenData(username=username)
    except JWTError:
        raise credentials_exception

    with Session(engine) as session:
        statement = select(User).where(User.username == username)
        user = session.exec(statement).first()

    if user is None:
        raise credentials_exception
    return user


def get_current_active_user(current_user: User = Depends(get_current_user)) -> User:
    if current_user.disabled:
        raise HTTPException(status_code=400, detail="Inactive user")
    return current_user


# Shorthand for dependencies
AuthenticatedUser = Depends(get_current_active_user)


def get_current_fresh_user(token: str = Depends(oauth2_scheme)) -> User:
    """Get current user and verify the token is fresh."""
    # Get user from token
    user = get_current_user(token)

    # Check if token is fresh
    try:
        payload = jwt.decode(token, SECRET_KEY, algorithms=[ALGORITHM])
        is_fresh = payload.get("fresh", False)

        if not is_fresh:
            raise HTTPException(
                status_code=status.HTTP_401_UNAUTHORIZED,
                detail="Token is not fresh. Please login again.",
                headers={"WWW-Authenticate": "Bearer"},
            )
    except JWTError:
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Could not validate credentials",
            headers={"WWW-Authenticate": "Bearer"},
        )

    return user


AuthenticatedFreshUser = Depends(get_current_fresh_user)


async def get_current_admin_user(
    current_user: User = Depends(get_current_user),
) -> User:
    if not current_user.superuser:
        raise HTTPException(status_code=status.HTTP_403_FORBIDDEN, detail="Not an admin user")
    return current_user


AdminUser = Depends(get_current_admin_user)


async def validate_token(token: str = Depends(oauth2_scheme)) -> User:
    user = get_current_user(token=token)
    return user
