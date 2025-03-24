"""Authentication core module."""

from collections.abc import Callable, Generator
from datetime import datetime, timedelta
from typing import TYPE_CHECKING, Any, Optional, TypeAlias, cast

from fastapi import Depends, HTTPException, status
from fastapi.security import OAuth2PasswordBearer
from jose import JWTError, jwt
from passlib.context import CryptContext
from pydantic import BaseModel
from sqlmodel import Field, Session, SQLModel, select

from .config.settings import settings
from .db import engine
from .models import UserCreate

if TYPE_CHECKING:
    from .models import UserCreate

# Type aliases for better readability
JWTData: TypeAlias = dict[str, Any]
JWTResponse: TypeAlias = dict[str, Any]
DependencyCallable: TypeAlias = Callable[..., Any]

pwd_context = CryptContext(schemes=["bcrypt"], deprecated="auto")
oauth2_scheme = OAuth2PasswordBearer(tokenUrl="token")

# Access settings with proper type hints
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


class User(SQLModel, table=True):  # type: ignore[call-arg]
    """User model for authentication."""

    id: int | None = Field(default=None, primary_key=True)
    username: str = Field(unique=True, index=True)
    email: str = Field(unique=True, index=True)
    full_name: str | None = None
    disabled: bool | None = Field(default=False)
    hashed_password: str
    created_at: datetime = Field(default_factory=datetime.utcnow)
    superuser: bool = Field(default=False)
    is_active: bool = True
    is_admin: bool = False
    is_superuser: bool = False

    @classmethod
    def create(cls, session: Session, user_in: UserCreate) -> "User":
        """Create a new user."""
        user = cls(
            username=user_in.username,
            email=user_in.email,
            hashed_password=get_password_hash(user_in.password),
            is_active=user_in.is_active,
            is_admin=user_in.is_admin,
            is_superuser=user_in.is_superuser,
        )
        session.add(user)
        session.flush()
        return user


class UserResponse(BaseModel):
    """User response model."""

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
    """Verify a password against its hash."""
    return pwd_context.verify(plain_password, hashed_password)


def get_password_hash(password: str) -> str:
    """Hash a password."""
    return pwd_context.hash(password)


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

    base_time = datetime.utcnow()
    delta = expires_delta or timedelta(minutes=15)
    expire = base_time + delta

    to_encode.update({"exp": expire})
    return jwt.encode(to_encode, SECRET_KEY, algorithm=ALGORITHM)


def create_refresh_token(data: JWTData, expires_delta: timedelta | None = None) -> str:
    """Create a new refresh token with the given data and expiration."""
    to_encode = data.copy()

    base_time = datetime.utcnow()
    delta = expires_delta or timedelta(days=7)
    expire = base_time + delta

    to_encode.update({"exp": expire})
    return jwt.encode(to_encode, SECRET_KEY, algorithm=ALGORITHM)


def decode_token(token: str) -> JWTResponse:
    """Decode a JWT token."""
    credentials_exception = HTTPException(
        status_code=status.HTTP_401_UNAUTHORIZED,
        detail="Could not validate credentials",
        headers={"WWW-Authenticate": "Bearer"},
    )

    try:
        payload = jwt.decode(token, SECRET_KEY, algorithms=[ALGORITHM])
        username: str = cast("str", payload.get("sub", ""))
        if username == "":
            raise credentials_exception
    except JWTError as err:
        raise credentials_exception from err

    return payload


def get_current_user(token: str = Depends(oauth2_scheme)) -> User:
    """Get the current user from the token."""
    credentials_exception = HTTPException(
        status_code=status.HTTP_401_UNAUTHORIZED,
        detail="Could not validate credentials",
        headers={"WWW-Authenticate": "Bearer"},
    )

    try:
        payload = jwt.decode(token, SECRET_KEY, algorithms=[ALGORITHM])
        username: str = cast("str", payload.get("sub", ""))
        if username == "":
            raise credentials_exception
    except JWTError as err:
        raise credentials_exception from err

    with Session(engine) as session:
        statement = select(User).where(User.username == username)
        user = session.exec(statement).first()

    if user is None:
        raise credentials_exception
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
    if not current_user.superuser:
        raise HTTPException(status_code=status.HTTP_403_FORBIDDEN, detail="Not an admin user")
    return current_user


def get_admin_user_dependency() -> DependencyCallable:
    """Dependency for authenticating admin users."""
    return cast(DependencyCallable, Depends(get_current_admin_user))


AdminUser = get_admin_user_dependency()


async def validate_token(token: str = Depends(oauth2_scheme)) -> User:
    user = get_current_user(token=token)
    return user
