"""User routes module."""

from typing import Any, List

from fastapi import APIRouter, Depends, HTTPException
from sqlmodel import Session, select

from ..auth_core import (
    get_current_active_user,
    get_current_admin_user,
    get_current_fresh_user,
    get_current_user,
)
from ..db import ActiveSession
from ..models.user import User, UserCreate, UserPasswordPatch, UserResponse
from ..utils.password import get_password_hash

router = APIRouter()


@router.get(
    "/",
    response_model=List[UserResponse],
    dependencies=[Depends(get_current_admin_user)],
)
async def list_users(*, session: Session = ActiveSession) -> Any:
    """List all users."""
    statement = select(User)
    users = session.exec(statement).all()
    return users


@router.post(
    "/",
    response_model=UserResponse,
    dependencies=[Depends(get_current_admin_user)],
)
async def create_user(*, session: Session = ActiveSession, user: UserCreate) -> Any:
    """Create a new user."""
    statement = select(User).where(User.username == user.username)
    db_user = session.exec(statement).first()
    if db_user:
        raise HTTPException(
            status_code=400,
            detail="Username already registered",
        )

    return User.create(user, session)


@router.patch(
    "/{user_id}/password/",
    response_model=UserResponse,
    dependencies=[Depends(get_current_fresh_user)],
)
async def update_user_password(
    *,
    user_id: int,
    session: Session = ActiveSession,
    patch: UserPasswordPatch,
    current_user: User = Depends(get_current_user),
) -> Any:
    """Update user password."""
    if patch.password != patch.password_confirm:
        raise HTTPException(
            status_code=400,
            detail="Passwords do not match",
        )

    user = session.get(User, user_id)
    if not user:
        raise HTTPException(
            status_code=404,
            detail="User not found",
        )

    if current_user.id != user.id and not current_user.is_admin:
        raise HTTPException(
            status_code=403,
            detail="Not enough permissions",
        )

    user.hashed_password = get_password_hash(patch.password)
    session.add(user)
    session.commit()
    session.refresh(user)
    return user


@router.get(
    "/{user_id_or_username}/",
    response_model=UserResponse,
    dependencies=[Depends(get_current_active_user)],
)
async def get_user_by_id_or_username(
    *,
    session: Session = ActiveSession,
    user_id_or_username: str | int,
) -> Any:
    """Get a user by ID or username."""
    if isinstance(user_id_or_username, int):
        user = session.get(User, user_id_or_username)
    else:
        statement = select(User).where(User.username == user_id_or_username)
        user = session.exec(statement).first()

    if not user:
        raise HTTPException(
            status_code=404,
            detail="User not found",
        )

    return user


@router.delete(
    "/{user_id}/",
    dependencies=[Depends(get_current_admin_user)],
)
def delete_user(
    *,
    session: Session = ActiveSession,
    user_id: int,
    current_user: User = Depends(get_current_user),
) -> Any:
    """Delete a user."""
    user = session.get(User, user_id)
    if not user:
        raise HTTPException(
            status_code=404,
            detail="User not found",
        )

    if current_user.id == user.id:
        raise HTTPException(
            status_code=400,
            detail="Cannot delete yourself",
        )

    session.delete(user)
    session.commit()
    return {"ok": True}
