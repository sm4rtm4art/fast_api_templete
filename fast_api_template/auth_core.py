"""Authentication core module."""

from collections.abc import Callable, Generator
from datetime import datetime, timedelta
from typing import Any, TypeAlias, cast

from fastapi import Depends, HTTPException, status
from fastapi.security import OAuth2PasswordBearer
from jose import JWTError, jwt
from passlib.context import CryptContext
from pydantic import BaseModel
from sqlmodel import Field, Session, SQLModel, select

from .config.settings import settings
from .db import engine
from .models.user import UserCreate, UserResponse

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


class User(SQLModel):
    """User model."""

    model_config = {"table": True}

    id: int | None = Field(default=None, primary_key=True)
    username: str = Field(unique=True, index=True)
    email: str
    hashed_password: str
    full_name: str | None = None
    is_active: bool = Field(default=True)
    is_superuser: bool = Field(default=False)
    is_admin: bool = Field(default=False)
    disabled: bool = Field(default=False)
    created_at: datetime = Field(default_factory=datetime.utcnow)

    @classmethod
    def create(cls, user_in: UserCreate, session: Session) -> "User":
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

    def to_response(self) -> UserResponse:
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
