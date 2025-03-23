from typing import Any

from fastapi import APIRouter

from .content import router as content_router
from .profile import router as profile_router
from .security import router as security_router
from .user import router as user_router

# Create and configure the main router
api_router = APIRouter(prefix="/api")

# Include all the sub-routers
api_router.include_router(security_router, tags=["security"])
api_router.include_router(user_router, prefix="/users", tags=["users"])
api_router.include_router(profile_router, prefix="/profile", tags=["profile"])
api_router.include_router(content_router, prefix="/content", tags=["content"])


@api_router.get("/")
async def index() -> Any:
    return {"message": "Hello World!"}
