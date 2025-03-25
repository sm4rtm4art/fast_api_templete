from typing import Any, List

from fastapi import APIRouter, Depends, HTTPException, status
from sqlmodel import Session, select

from ..auth_core import (
    User,
    UserPasswordPatch,
    get_current_active_user,
    get_current_admin_user,
    get_current_fresh_user,
    get_current_user,
    get_password_hash,
)
from ..db import ActiveSession
from ..models.user import UserCreate, UserResponse

router = APIRouter()


@router.get(
    "/",
    response_model=List[UserResponse],
    dependencies=[Depends(get_current_admin_user)],
)
async def list_users(*, session: Session = ActiveSession) -> Any:
    """List all users."""
    users = session.exec(select(User)).all()
    return users


@router.post(
    "/",
    response_model=UserResponse,
    dependencies=[Depends(get_current_admin_user)],
)
async def create_user(*, session: Session = ActiveSession, user: UserCreate) -> Any:
    """Create a new user."""
    # verify user with username doesn't already exist
    existing = session.exec(select(User).where(User.username == user.username)).first()
    if existing:
        raise HTTPException(status_code=422, detail="Username already exists")

    # verify user with email doesn't already exist
    existing = session.exec(select(User).where(User.email == user.email)).first()
    if existing:
        raise HTTPException(status_code=422, detail="Email already exists")

    # create user
    new_user = User(
        username=user.username,
        email=user.email,
        hashed_password=get_password_hash(user.password),
        full_name=user.full_name,
        is_active=user.is_active,
        is_superuser=user.is_superuser,
        is_admin=user.is_admin,
        disabled=user.disabled,
    )
    session.add(new_user)
    session.commit()
    session.refresh(new_user)
    return new_user


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
    """Update a user's password."""
    # verify the user exists
    user = session.get(User, user_id)
    if not user:
        raise HTTPException(status_code=404, detail="User not found")

    # check if user is trying to update their own password
    if current_user.id == user_id:
        # check if user is admin or superuser
        if current_user.is_admin or current_user.is_superuser:
            if patch.password != patch.password_confirm:
                raise HTTPException(status_code=422, detail="Passwords don't match")

    # update the password
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
    if isinstance(user_id_or_username, int) or user_id_or_username.isdigit():
        user = session.get(User, int(user_id_or_username))
    else:
        user = session.exec(select(User).where(User.username == user_id_or_username)).first()

    if not user:
        raise HTTPException(status_code=404, detail="User not found")

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
    # verify the user exists
    user = session.get(User, user_id)
    if not user:
        raise HTTPException(status_code=404, detail="User not found")

    # Don't allow deleting yourself
    if user.id == current_user.id:
        raise HTTPException(status_code=403, detail="Cannot delete yourself")

    # delete the user
    session.delete(user)
    session.commit()
    return {"status": "success", "message": f"User {user_id} deleted"}
