"""Database configuration and session management."""

from collections.abc import Generator
from contextlib import contextmanager
from typing import Optional

from fastapi import Depends
from sqlalchemy.engine import Engine
from sqlmodel import Session, SQLModel

from .database import engine


def create_db_and_tables(custom_engine: Optional[Engine] = None) -> None:
    """Create database tables from SQLModel metadata.

    Args:
        custom_engine: Optional engine to use instead of the default
    """
    # Import all models to ensure they are registered with SQLModel metadata
    # These imports are here to avoid circular imports
    from .models.user import User  # noqa
    from .models.content import Content  # noqa

    target_engine = custom_engine or engine
    SQLModel.metadata.create_all(target_engine)


@contextmanager
def get_session() -> Generator[Session, None, None]:
    """Get a database session.

    Yields:
        Session: A database session
    """
    session = Session(engine)
    try:
        yield session
    finally:
        session.close()


# Modified dependency function that doesn't use context manager
def get_db() -> Generator[Session, None, None]:
    """Get a database session for FastAPI dependency injection.

    Yields:
        Session: A database session
    """
    session = Session(engine)
    try:
        yield session
    finally:
        session.close()


ActiveSession = Depends(get_db)
