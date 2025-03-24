"""FastAPI application definition."""

import os
import time
from typing import Any, List

from fastapi import Depends, FastAPI
from fastapi.middleware.cors import CORSMiddleware

from .auth.auth import User, get_current_active_user
from .config import settings
from .db import create_db_and_tables
from .routes import api_router
from .routes.auth import router as auth_router


def read(*paths: str, **kwargs: Any) -> Any:
    """Read the contents of a text file safely.
    >>> read("VERSION")
    """
    content = ""
    with open(
        os.path.join(os.path.dirname(__file__), *paths),
        encoding=kwargs.get("encoding", "utf8"),
    ) as open_file:
        content = open_file.read().strip()
    return content


description = """
fast_api_template API helps you do awesome stuff. 🚀
"""

app = FastAPI(
    title=settings.SERVER_NAME,
    description=settings.SERVER_DESCRIPTION,
    version=settings.SERVER_VERSION,
    docs_url=settings.SERVER_DOCS_URL,
)

# Handle CORS origins
origins: List[str] = []


def parse_cors_origin(value: Any) -> List[str]:
    """Parse CORS origin value into a list of strings."""
    if isinstance(value, str):
        return [origin.strip() for origin in value.split(",") if origin.strip()]
    if isinstance(value, (list, tuple)):
        return [str(origin).strip() for origin in value if str(origin).strip()]
    origin = str(value).strip()
    return [origin] if origin else []


if settings.SERVER_CORS_ORIGINS:
    origins = parse_cors_origin(settings.SERVER_CORS_ORIGINS)

app.add_middleware(
    CORSMiddleware,
    allow_origins=origins,
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

app.include_router(api_router)
app.include_router(auth_router)


@app.on_event("startup")
async def on_startup() -> None:
    """Create database tables on startup."""
    create_db_and_tables()


@app.get("/health")
async def health_check() -> dict[str, Any]:
    """Health check endpoint."""
    return {
        "status": "ok",
        "timestamp": time.time(),
    }


@app.get("/")
async def root() -> dict[str, Any]:
    """Root endpoint."""
    return {
        "message": "Welcome to fast_api_template API",
        "docs": settings.SERVER_DOCS_URL,
    }


@app.get("/me")
async def read_users_me(current_user: User = Depends(get_current_active_user)) -> User:
    """Get current user."""
    return current_user
