from typing import Any

from fastapi import APIRouter, Depends

from ..auth_core import User, UserResponse, get_current_active_user

router = APIRouter()


@router.get("/", response_model=UserResponse)
async def my_profile(current_user: User = Depends(get_current_active_user)) -> Any:
    return current_user
