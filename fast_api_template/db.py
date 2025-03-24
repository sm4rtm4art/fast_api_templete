from collections.abc import Generator
from contextlib import contextmanager

from fastapi import Depends
from sqlmodel import SQLModel, Session, create_engine

from .config import settings

DATABASE_URL = settings.db.uri
engine = create_engine(DATABASE_URL, echo=settings.db.echo)


def create_db_and_tables(custom_engine=None) -> None:
    """Create database tables from SQLModel metadata.

    Args:
        custom_engine: Optional engine to use instead of the default
    """
    target_engine = custom_engine or engine
    SQLModel.metadata.create_all(target_engine)


@contextmanager
def get_session() -> Generator[Session, None, None]:
    session = Session(engine)
    try:
        yield session
    finally:
        session.close()


def get_db() -> Generator[Session, None, None]:
    with get_session() as session:
        yield session


ActiveSession = Depends(get_db)
