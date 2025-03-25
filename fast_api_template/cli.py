"""Command line interface module."""

import typer
from rich.console import Console
from rich.traceback import install as install_rich_traceback

from .auth_core import User
from .db import create_db_and_tables, get_session
from .models import UserCreate

# Install rich traceback handler
install_rich_traceback()

# Create console for rich output
console = Console()

# Create typer app
app = typer.Typer()


@app.command()
def shell() -> None:
    """Start an IPython shell with the application context."""
    try:
        from IPython import embed

        embed(colors="neutral")
    except ImportError:
        msg = "IPython is not installed. Please install it with: pip install ipython"
        console.print(f"[red]{msg}[/red]")
        raise typer.Exit(1)


@app.command()
def create_user(
    username: str,
    email: str,
    password: str,
    is_admin: bool = False,
    is_active: bool = True,
    is_superuser: bool = False,
) -> None:
    """Create a new user."""
    create_db_and_tables()

    user_in = UserCreate(
        username=username,
        email=email,
        password=password,
        is_admin=is_admin,
        is_active=is_active,
        is_superuser=is_superuser,
    )

    with get_session() as session:
        user = User.create(user_in=user_in, session=session)
        session.commit()

    console.print(f"[green]Created user:[/green] {user}")


if __name__ == "__main__":
    app()
