"""Authentication routes module."""

from datetime import timedelta
from typing import Any

from fastapi import APIRouter, Depends, HTTPException, status
from fastapi.security import OAuth2PasswordRequestForm
from sqlmodel import Session, select

from fast_api_template.auth_core import (
    Token,
    User,
    authenticate_user,
    create_access_token,
    get_current_user,
)
from fast_api_template.config.settings import settings
from fast_api_template.db import get_session
from fast_api_template.models.user import UserCreate, UserResponse

router = APIRouter()


@router.post("/register", response_model=UserResponse)
async def register(
    user_in: UserCreate,
    session: Session = Depends(get_session),
) -> Any:
    """Register a new user."""
    # verify user with username doesn't already exist
    existing = session.exec(select(User).where(User.username == user_in.username)).first()
    if existing:
        raise HTTPException(
            status_code=status.HTTP_422_UNPROCESSABLE_ENTITY,
            detail="Username already exists",
        )

    # verify user with email doesn't already exist
    existing = session.exec(select(User).where(User.email == user_in.email)).first()
    if existing:
        raise HTTPException(
            status_code=status.HTTP_422_UNPROCESSABLE_ENTITY,
            detail="Email already exists",
        )

    user = User.create(user_in=user_in, session=session)
    return user.to_response()


@router.post("/login", response_model=Token)
async def login(
    form_data: OAuth2PasswordRequestForm = Depends(),
    session: Session = Depends(get_session),
) -> Any:
    """Login user and return access token."""
    user = authenticate_user(form_data.username, form_data.password)
    if not user or not isinstance(user, User):
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Incorrect username or password",
            headers={"WWW-Authenticate": "Bearer"},
        )
    if not user.is_active:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="Inactive user",
        )

    access_token_expires = timedelta(minutes=settings.jwt.access_token_expire_minutes)
    refresh_token_expires = timedelta(minutes=settings.jwt.refresh_token_expire_minutes)

    access_token = create_access_token(
        data={"sub": user.username},
        expires_delta=access_token_expires,
    )

    refresh_token = create_access_token(
        data={"sub": user.username},
        expires_delta=refresh_token_expires,
    )

    return {"access_token": access_token, "refresh_token": refresh_token, "token_type": "bearer"}


@router.post("/refresh", response_model=Token)
async def refresh_token(
    current_user: User = Depends(get_current_user),
) -> Any:
    """Refresh access token."""
    access_token_expires = timedelta(minutes=settings.jwt.access_token_expire_minutes)
    refresh_token_expires = timedelta(minutes=settings.jwt.refresh_token_expire_minutes)

    access_token = create_access_token(
        data={"sub": current_user.username},
        expires_delta=access_token_expires,
    )

    refresh_token = create_access_token(
        data={"sub": current_user.username},
        expires_delta=refresh_token_expires,
    )

    return {"access_token": access_token, "refresh_token": refresh_token, "token_type": "bearer"}
