from typing import Any

from fastapi import APIRouter

from .auth_routes import router as auth_router
from .content import router as content_router
from .profile import router as profile_router
from .user import router as user_router

# Create and configure the main router without a prefix
api_router = APIRouter()

# Include all the sub-routers
api_router.include_router(auth_router, tags=["authentication"])
api_router.include_router(user_router, prefix="/user", tags=["users"])
api_router.include_router(profile_router, prefix="/profile", tags=["profile"])
api_router.include_router(content_router, prefix="/content", tags=["content"])


@api_router.get("/")
async def index() -> Any:
    return {"message": "Hello World!"}
