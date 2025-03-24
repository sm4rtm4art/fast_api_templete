import os
import time
from typing import Any

from fastapi import Depends, FastAPI
from fastapi.middleware.cors import CORSMiddleware

from .config import settings
from .db import create_db_and_tables
from .routes import api_router
from .routes.security import router as security_router
from .security import get_current_active_user


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
    title=settings.server.name,
    description=settings.server.description,
    version=settings.server.version,
    docs_url=settings.server.docs_url,
)

if settings.server.cors_origins:
    # Check if cors_origins is a string or list
    origins = settings.server.cors_origins
    if isinstance(origins, str):
        # Split string by comma and strip whitespace
        allow_origins = [origin.strip() for origin in origins.split(",")]
    else:
        # Use the list as is
        allow_origins = origins

    app.add_middleware(
        CORSMiddleware,
        allow_origins=allow_origins,
        allow_credentials=True,
        allow_methods=["*"],
        allow_headers=["*"],
    )

app.include_router(api_router)
app.include_router(security_router, tags=["authentication"])


@app.on_event("startup")
async def on_startup() -> None:
    """Initialize the database and create tables on startup."""
    create_db_and_tables()


@app.get("/health")
async def health_check() -> dict[str, Any]:
    """Health check endpoint."""
    return {
        "status": "healthy",
        "timestamp": time.time(),
    }


@app.get("/")
async def root() -> dict[str, Any]:
    """Root endpoint."""
    return {
        "message": "Hello World!",
    }


@app.get("/me")
async def read_users_me(current_user: Any = Depends(get_current_active_user)) -> Any:
    """Returns information about the current authenticated user."""
    return current_user
