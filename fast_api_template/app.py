import os
import time

from fastapi import Depends, FastAPI
from sqlmodel import Session, select
from starlette.middleware.cors import CORSMiddleware

from .config import settings
from .db import create_db_and_tables, engine, get_session
from .routes import main_router


def read(*paths, **kwargs):
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
    title="fast_api_template",
    description=description,
    version=read("VERSION"),
    terms_of_service="http://fast_api_template.com/terms/",
    contact={
        "name": "sm4rtm4art",
        "url": "http://fast_api_template.com/contact/",
        "email": "sm4rtm4art@fast_api_template.com",
    },
    license_info={
        "name": "The Unlicense",
        "url": "https://unlicense.org",
    },
)

if settings.server and settings.server.get("cors_origins", None):
    app.add_middleware(
        CORSMiddleware,
        allow_origins=settings.server.cors_origins,
        allow_credentials=settings.get("server.cors_allow_credentials", True),
        allow_methods=settings.get("server.cors_allow_methods", ["*"]),
        allow_headers=settings.get("server.cors_allow_headers", ["*"]),
    )

app.include_router(main_router)


@app.on_event("startup")
def on_startup():
    create_db_and_tables(engine)


@app.get("/health", tags=["Health"])
async def health_check(session: Session = Depends(get_session)) -> dict[str, str]:
    """
    Health check endpoint that also verifies database connectivity.
    """
    # Check database connection
    try:
        # Simple query to check DB connection
        session.exec(select(1)).one()
        db_status = "healthy"
    except Exception:
        db_status = "unhealthy"

    return {
        "status": "healthy",
        "timestamp": time.strftime("%Y-%m-%d %H:%M:%S", time.gmtime()),
        "database": db_status,
        "version": read("VERSION"),
    }
