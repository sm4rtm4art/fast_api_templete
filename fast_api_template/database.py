"""Database engine configuration."""

from typing import Dict

from sqlalchemy.engine import Engine
from sqlmodel import create_engine

from .config.settings import settings

# Access settings with proper type hints
DATABASE_URL: str
try:
    DATABASE_URL = settings.database.url
except AttributeError:
    DATABASE_URL = settings.DATABASE_URL

DB_ECHO: bool = getattr(settings.database, "echo", False)
DB_CONNECT_ARGS: Dict[str, bool] = {"check_same_thread": False}

engine: Engine = create_engine(
    DATABASE_URL,
    echo=DB_ECHO,
    connect_args=DB_CONNECT_ARGS,
)
