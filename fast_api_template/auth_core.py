"""Authentication core module."""

from collections.abc import Callable
from datetime import UTC, datetime, timedelta
from typing import Any, TypeAlias, cast

from fastapi import Depends, HTTPException, status
from fastapi.security import OAuth2PasswordBearer
from jose import JWTError, jwt
from pydantic import BaseModel
from sqlmodel import Session, select

from .config import settings
from .database import engine
from .models.user import User
from .utils.password import verify_password

# Type aliases for better readability
JWTData: TypeAlias = dict[str, Any]
JWTResponse: TypeAlias = dict[str, Any]
DependencyCallable: TypeAlias = Callable[..., Any]

oauth2_scheme = OAuth2PasswordBearer(tokenUrl="token")

# Access JWT settings through the unified settings object
SECRET_KEY: str = settings.jwt.secret_key
ALGORITHM: str = settings.jwt.algorithm


class Token(BaseModel):
    """Token response model."""

    access_token: str
    refresh_token: str
    token_type: str


class RefreshToken(BaseModel):
    """Refresh token request model."""

    refresh_token: str


class TokenData(BaseModel):
    """Token data model."""

    username: str | None = None


def authenticate_user(username: str, password: str) -> User | bool:
    """Authenticate a user."""
    with Session(engine) as session:
        statement = select(User).where(User.username == username)
        user = session.exec(statement).first()
        if not user:
            return False
        if not verify_password(password, user.hashed_password):
            return False
        return user


def create_access_token(data: JWTData, expires_delta: timedelta | None = None) -> str:
    """Create a new access token with the given data and expiration."""
    to_encode = data.copy()

    base_time = datetime.now(UTC)
    delta = expires_delta or timedelta(minutes=15)
    expire = base_time + delta

    to_encode.update({"exp": expire})
    return jwt.encode(to_encode, SECRET_KEY, algorithm=ALGORITHM)


def create_refresh_token(data: JWTData, expires_delta: timedelta | None = None) -> str:
    """Create a new refresh token with the given data and expiration."""
    to_encode = data.copy()

    base_time = datetime.now(UTC)
    delta = expires_delta or timedelta(days=7)
    expire = base_time + delta

    to_encode.update({"exp": expire})
    return jwt.encode(to_encode, SECRET_KEY, algorithm=ALGORITHM)


def decode_token(token: str) -> JWTResponse:
    """Decode a JWT token."""
    error = HTTPException(
        status_code=status.HTTP_401_UNAUTHORIZED,
        detail="Could not validate credentials",
        headers={"WWW-Authenticate": "Bearer"},
    )

    try:
        payload = jwt.decode(token, SECRET_KEY, algorithms=[ALGORITHM])
        username: str = cast("str", payload.get("sub", ""))
        if username == "":
            raise error
    except JWTError as err:
        raise error from err

    return payload


def get_current_user(token: str = Depends(oauth2_scheme)) -> User:
    """Get the current user from the token."""
    error = HTTPException(
        status_code=status.HTTP_401_UNAUTHORIZED,
        detail="Could not validate credentials",
        headers={"WWW-Authenticate": "Bearer"},
    )

    try:
        payload = decode_token(token)
        username: str = cast("str", payload.get("sub", ""))
        if username == "":
            raise error
        token_data = TokenData(username=username)
    except JWTError as err:
        raise error from err

    # Get the session and query for the user
    with Session(engine) as session:
        statement = select(User).where(User.username == token_data.username)
        user = session.exec(statement).first()

    if user is None:
        raise error

    return user


def get_current_active_user(current_user: User = Depends(get_current_user)) -> User:
    """Get the current active user."""
    if current_user.disabled:
        raise HTTPException(status_code=400, detail="Inactive user")
    return current_user


def get_authenticated_user_dependency() -> DependencyCallable:
    """Dependency for authenticating users."""
    return cast(DependencyCallable, Depends(get_current_active_user))


AuthenticatedUser = get_authenticated_user_dependency()


def get_current_fresh_user(token: str = Depends(oauth2_scheme)) -> User:
    """Get current user and verify the token is fresh."""
    user = get_current_user(token)

    try:
        payload = jwt.decode(token, SECRET_KEY, algorithms=[ALGORITHM])
        is_fresh = payload.get("fresh", False)

        if not is_fresh:
            raise HTTPException(
                status_code=status.HTTP_401_UNAUTHORIZED,
                detail="Token is not fresh. Please login again.",
                headers={"WWW-Authenticate": "Bearer"},
            )
    except JWTError as err:
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Could not validate credentials",
            headers={"WWW-Authenticate": "Bearer"},
        ) from err

    return user


def get_authenticated_fresh_user_dependency() -> DependencyCallable:
    """Dependency for authenticating users with fresh tokens."""
    return cast(DependencyCallable, Depends(get_current_fresh_user))


AuthenticatedFreshUser = get_authenticated_fresh_user_dependency()


async def get_current_admin_user(
    current_user: User = Depends(get_current_user),
) -> User:
    """Get current admin user."""
    if not current_user.is_admin and not current_user.is_superuser:
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN,
            detail="The user doesn't have enough privileges",
        )
    return current_user


def get_admin_user_dependency() -> DependencyCallable:
    """Dependency for authenticating admin users."""
    return cast(DependencyCallable, Depends(get_current_admin_user))


AdminUser = get_admin_user_dependency()


async def validate_token(token: str = Depends(oauth2_scheme)) -> User:
    user = get_current_user(token=token)
    return user
