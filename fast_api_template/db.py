from collections.abc import Generator
from contextlib import contextmanager
from typing import Any

from fastapi import Depends
from sqlmodel import SQLModel, Session, create_engine

from .config import settings

DATABASE_URL = settings.db.url
engine = create_engine(DATABASE_URL, echo=settings.db.echo)


def create_db_and_tables() -> None:
    SQLModel.metadata.create_all(engine)


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


ActiveSession = Depends(get_session)
