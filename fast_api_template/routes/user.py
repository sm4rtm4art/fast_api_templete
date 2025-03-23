from typing import Any

from fastapi import APIRouter, Depends, HTTPException
from sqlmodel import Session, select

from ..db import ActiveSession
from ..security import (
    AdminUser,
    AuthenticatedFreshUser,
    AuthenticatedUser,
    User,
    UserCreate,
    UserPasswordPatch,
    UserResponse,
    get_current_user,
    get_password_hash,
)

router = APIRouter()


@router.get("/", response_model=list[UserResponse], dependencies=[Depends(AdminUser)])
async def list_users(*, session: Session = ActiveSession) -> Any:
    """List all users."""
    users = session.exec(select(User)).all()
    return users


@router.post("/", response_model=UserResponse, dependencies=[Depends(AdminUser)])
async def create_user(*, session: Session = ActiveSession, user: UserCreate) -> Any:
    """Create a new user."""
    # verify user with username doesn't already exist
    existing = session.exec(select(User).where(User.username == user.username)).first()
    if existing:
        raise HTTPException(status_code=422, detail="Username already exists")

    db_user = User(**user.dict())
    session.add(db_user)
    session.commit()
    session.refresh(db_user)
    return db_user


@router.patch(
    "/{user_id}/password/",
    response_model=UserResponse,
    dependencies=[Depends(AuthenticatedFreshUser)],
)
async def update_user_password(
    *,
    user_id: int,
    session: Session = ActiveSession,
    patch: UserPasswordPatch,
    current_user: User = Depends(get_current_user),
) -> Any:
    """Update a user's password."""
    # Query the user
    user = session.get(User, user_id)
    if not user:
        raise HTTPException(status_code=404, detail="User not found")

    # Check the user can update the password
    if user.id != current_user.id and not current_user.superuser:
        raise HTTPException(status_code=403, detail="You can't update this user password")

    if not patch.password == patch.password_confirm:
        raise HTTPException(status_code=400, detail="Passwords don't match")

    # Update the password
    user.password = get_password_hash(patch.password)

    # Commit the session
    session.commit()
    session.refresh(user)
    return user


@router.get(
    "/{user_id_or_username}/",
    response_model=UserResponse,
    dependencies=[Depends(AuthenticatedUser)],
)
async def get_user_by_id_or_username(*, session: Session = ActiveSession, user_id_or_username: str | int) -> Any:
    """Get a user by ID or username."""
    query = None
    if isinstance(user_id_or_username, int):
        query = select(User).where(User.id == user_id_or_username)
    else:
        query = select(User).where(User.username == user_id_or_username)

    user = session.exec(query).first()
    if not user:
        raise HTTPException(status_code=404, detail="User not found")
    return user


@router.delete("/{user_id}/", dependencies=[Depends(AdminUser)])
def delete_user(
    *, session: Session = ActiveSession, user_id: int, current_user: User = Depends(get_current_user)
) -> Any:
    """Delete a user."""
    user = session.get(User, user_id)
    if not user:
        raise HTTPException(status_code=404, detail="User not found")

    # Check the user is not deleting himself
    if user.id == current_user.id:
        raise HTTPException(status_code=403, detail="You can't delete yourself")

    session.delete(user)
    session.commit()
    return {"ok": True}
