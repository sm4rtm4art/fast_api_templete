"""Test configuration module."""

import contextlib
import os
import sys
from typing import Any, Generator

import pytest
from fastapi.testclient import TestClient
from sqlalchemy.exc import IntegrityError
from sqlmodel import Session, SQLModel, create_engine
from typer.testing import CliRunner

# This next line ensures tests uses its own database and settings environment
os.environ["FORCE_ENV_FOR_DYNACONF"] = "testing"  # noqa
# WARNING: Ensure imports from `fast_api_template` comes after this line
from fast_api_template import app, db  # noqa
from fast_api_template.cli import app as cli_app  # noqa
from fast_api_template.config.settings import settings
from fast_api_template.auth_core import User
from fast_api_template.models import UserCreate


def create_user(username: str, password: str) -> None:
    """Create a test user."""
    with db.get_session() as session:
        user_in = UserCreate(
            username=username,
            email=f"{username}@example.com",
            password=password,
            is_admin=True,
            is_active=True,
            is_superuser=True,
        )
        User.create(session, user_in)
        session.commit()


# each test runs on cwd to its temp dir
@pytest.fixture(autouse=True)
def go_to_tmpdir(request: pytest.FixtureRequest) -> Generator[None, None, None]:
    # Get the fixture dynamically by its name.
    tmpdir = request.getfixturevalue("tmpdir")
    # ensure local test created packages can be imported
    sys.path.insert(0, str(tmpdir))
    # Chdir only for the duration of the test.
    with tmpdir.as_cwd():
        yield


@pytest.fixture(scope="function", name="app")
def _app() -> Any:
    return app


@pytest.fixture(scope="function", name="cli")
def _cli() -> Any:
    return cli_app


@pytest.fixture(scope="function")
def api_client() -> TestClient:
    return TestClient(app)


@pytest.fixture(scope="function")
def api_client_authenticated() -> TestClient:
    with contextlib.suppress(IntegrityError):
        create_user("admin", password="admin")

    client = TestClient(app)
    token = client.post(
        "/token",
        data={"username": "admin", "password": "admin"},
        headers={"Content-Type": "application/x-www-form-urlencoded"},
    ).json()["access_token"]
    client.headers["Authorization"] = f"Bearer {token}"
    return client


@pytest.fixture(scope="function")
def cli_client() -> CliRunner:
    return CliRunner()


@pytest.fixture
def cli_runner() -> CliRunner:
    """Create a CLI runner."""
    return CliRunner()


@pytest.fixture
def test_user(cli_runner: CliRunner) -> None:
    """Create a test user."""
    result = cli_runner.invoke(
        cli_app,
        [
            "create-user",
            "test",
            "--email",
            "test@example.com",
            "--password",
            "test",
        ],
    )
    assert result.exit_code == 0


def remove_db() -> None:
    """Remove the test database."""
    try:
        db_path = settings.DATABASE_URL.replace("sqlite:///", "")
        os.remove(db_path)
    except FileNotFoundError:
        pass


@pytest.fixture(autouse=True)
def setup_db() -> Generator[None, None, None]:
    """Set up the test database."""
    remove_db()
    yield
    remove_db()


@pytest.fixture
def session() -> Generator[Session, None, None]:
    """Create a database session."""
    engine = create_engine(settings.DATABASE_URL)
    SQLModel.metadata.create_all(engine)
    with Session(engine) as session:
        yield session
