"""Test configuration module."""

import os
from typing import Any, Generator

import pytest
from fastapi import FastAPI
from fastapi.testclient import TestClient
from sqlalchemy.exc import IntegrityError
from sqlmodel import Session, SQLModel, create_engine, select
from typer.testing import CliRunner

from fast_api_template.models.user import User
from fast_api_template.utils.password import get_password_hash

# Set environment variables for testing
os.environ["FORCE_ENV_FOR_DYNACONF"] = "testing"
os.environ["FAST_API_TEMPLATE_SETTINGS_FILE"] = "tests/test_settings.toml"

# Define test database connection
TEST_DB_URL = "sqlite:///test.db"
TEST_ENGINE = create_engine(TEST_DB_URL, connect_args={"check_same_thread": False})


# Override the get_db dependency for testing
def override_get_db() -> Generator[Session, None, None]:
    with Session(TEST_ENGINE) as session:
        yield session


def remove_db() -> None:
    """Remove the test database."""
    try:
        db_path = "test.db"
        if os.path.exists(db_path):
            os.remove(db_path)
    except FileNotFoundError:
        pass


@pytest.fixture(scope="session", autouse=True)
def setup_db() -> Generator[None, None, None]:
    """Set up database for testing."""
    # Remove any existing test database
    remove_db()

    # Create test database and tables
    SQLModel.metadata.create_all(TEST_ENGINE)

    # Create a test user
    with Session(TEST_ENGINE) as session:
        try:
            user = User(
                username="admin",
                email="admin@example.com",
                hashed_password=get_password_hash("admin"),
                is_active=True,
                is_admin=True,
                is_superuser=True,
            )
            session.add(user)
            session.commit()
            session.refresh(user)

            # Verify user was created correctly
            statement = select(User).where(User.username == "admin")
            result = session.exec(statement).first()
            if result:
                print(f"\nTest user created and verified: {result.username}")
            else:
                print("\nERROR: Test user not found after creation")
        except IntegrityError:
            session.rollback()
            print("\nTest user already exists")

    # Return to tests
    yield

    # Clean up
    remove_db()


@pytest.fixture(scope="function")
def app() -> FastAPI:
    """Get a fresh copy of the application for testing."""
    # Import the app module
    from fast_api_template import app as app_instance
    from fast_api_template.db import get_db

    # Override the get_db dependency
    app_instance.dependency_overrides[get_db] = override_get_db

    # Also override the engine in auth_core
    from fast_api_template import auth_core

    auth_core.engine = TEST_ENGINE

    return app_instance


@pytest.fixture(scope="function")
def api_client(app: FastAPI) -> TestClient:
    """Create a test client."""
    return TestClient(app)


@pytest.fixture(scope="function")
def api_client_authenticated(api_client: TestClient) -> TestClient:
    """Create an authenticated test client."""
    # Create auth token
    try:
        response = api_client.post(
            "/token",
            data={"username": "admin", "password": "admin"},
            headers={"Content-Type": "application/x-www-form-urlencoded"},
        )

        # Check if authentication was successful
        auth_error_msg = f"Authentication failed: {response.text}"
        assert response.status_code == 200, auth_error_msg

        # Set authorization header
        token = response.json()["access_token"]
        api_client.headers["Authorization"] = f"Bearer {token}"
    except Exception as e:
        print(f"Failed to authenticate: {str(e)}")
        # For debugging
        with Session(TEST_ENGINE) as session:
            result = session.exec(select(User)).all()
            print(f"Available users: {[u.username for u in result]}")
        raise

    return api_client


@pytest.fixture(scope="function")
def cli_client() -> CliRunner:
    """Create a CLI runner."""
    return CliRunner()


@pytest.fixture(scope="function")
def cli() -> Any:
    """Create a CLI app."""
    from fast_api_template.cli import app as cli_app

    return cli_app


@pytest.fixture
def session() -> Generator[Session, None, None]:
    """Create a database session."""
    with Session(TEST_ENGINE) as session:
        yield session
