"""Profile routes module."""

from fastapi import APIRouter, Depends

from ..auth_core import get_current_user
from ..models.user import User, UserResponse

router = APIRouter(prefix="/profile", tags=["profile"])


@router.get("/me", response_model=UserResponse)
async def read_users_me(current_user: User = Depends(get_current_user)) -> User:
    """Get current user profile."""
    return current_user
