import os
import time
from typing import Any

from fastapi import Depends, FastAPI
from fastapi.middleware.cors import CORSMiddleware

from .config import settings
from .db import create_db_and_tables
from .routes import api_router
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
    title=settings.app.name,
    description=settings.app.description,
    version=settings.app.version,
    docs_url=settings.app.docs_url,
)

if settings.app.cors_origins:
    app.add_middleware(
        CORSMiddleware,
        allow_origins=[origin.strip() for origin in settings.app.cors_origins.split(",")],
        allow_credentials=True,
        allow_methods=["*"],
        allow_headers=["*"],
    )

app.include_router(api_router)


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


@app.get("/me")
async def read_users_me(current_user: Any = Depends(get_current_active_user)) -> Any:
    """Returns information about the current authenticated user."""
    return current_user
