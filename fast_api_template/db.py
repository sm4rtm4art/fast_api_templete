"""Database configuration and session management."""

from collections.abc import Generator
from contextlib import contextmanager
from typing import Optional

from fastapi import Depends
from sqlalchemy.engine import Engine
from sqlmodel import Session, SQLModel, create_engine

from .config.settings import settings

# Access settings with proper type hints
DATABASE_URL: str = settings.database.url
DB_ECHO: bool = settings.database.echo
DB_CONNECT_ARGS: dict = {"check_same_thread": False}

engine: Engine = create_engine(
    DATABASE_URL,
    echo=DB_ECHO,
    connect_args=DB_CONNECT_ARGS,
)


def create_db_and_tables(custom_engine: Optional[Engine] = None) -> None:
    """Create database tables from SQLModel metadata.

    Args:
        custom_engine: Optional engine to use instead of the default
    """
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


def get_db() -> Generator[Session, None, None]:
    """Get a database session for FastAPI dependency injection.

    Yields:
        Session: A database session
    """
    with get_session() as session:
        yield session


ActiveSession = Depends(get_db)
