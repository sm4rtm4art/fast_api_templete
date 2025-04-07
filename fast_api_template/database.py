"""Database engine configuration."""

from typing import Any, Dict

from sqlalchemy.engine import Engine
from sqlmodel import create_engine

# Import the unified settings object
from .config import settings

# Access settings through the unified settings object
DATABASE_URL: str = settings.database.url
DB_ECHO: bool = settings.database.echo

# Only use check_same_thread for SQLite
connect_args: Dict[str, Any] = {}
if DATABASE_URL.startswith("sqlite"):
    connect_args["check_same_thread"] = False

engine: Engine = create_engine(
    DATABASE_URL,
    echo=DB_ECHO,
    connect_args=connect_args,
)
