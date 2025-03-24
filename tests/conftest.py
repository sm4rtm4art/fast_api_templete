import contextlib
import os
import platform
import sys
import time
from pathlib import Path

import pytest
from fastapi.testclient import TestClient
from sqlalchemy.exc import IntegrityError
from typer.testing import CliRunner

# This next line ensures tests uses its own database and settings environment
os.environ["FORCE_ENV_FOR_DYNACONF"] = "testing"  # noqa
# WARNING: Ensure imports from `fast_api_template` comes after this line
from fast_api_template import app, settings, db  # noqa
from fast_api_template.cli import create_user, cli  # noqa


# each test runs on cwd to its temp dir
@pytest.fixture(autouse=True)
def go_to_tmpdir(request):
    # Get the fixture dynamically by its name.
    tmpdir = request.getfixturevalue("tmpdir")
    # ensure local test created packages can be imported
    sys.path.insert(0, str(tmpdir))
    # Chdir only for the duration of the test.
    with tmpdir.as_cwd():
        yield


@pytest.fixture(scope="function", name="app")
def _app():
    return app


@pytest.fixture(scope="function", name="cli")
def _cli():
    return cli


@pytest.fixture(scope="function", name="settings")
def _settings():
    return settings


@pytest.fixture(scope="function")
def api_client():
    return TestClient(app)


@pytest.fixture(scope="function")
def api_client_authenticated():
    with contextlib.suppress(IntegrityError):
        create_user("admin", "admin", superuser=True)

    client = TestClient(app)
    token = client.post(
        "/token",
        data={"username": "admin", "password": "admin"},
        headers={"Content-Type": "application/x-www-form-urlencoded"},
    ).json()["access_token"]
    client.headers["Authorization"] = f"Bearer {token}"
    return client


@pytest.fixture(scope="function")
def cli_client():
    return CliRunner()


def remove_db():
    # Get database path
    db_path = Path("testing.db")

    # Close any open connections before removing the file
    db.engine.dispose()

    # Give Windows a moment to release file locks
    if platform.system() == "Windows":
        time.sleep(1)

    # Try to remove the file multiple times on Windows
    max_attempts = 5 if platform.system() == "Windows" else 1

    for attempt in range(max_attempts):
        try:
            if db_path.exists():
                db_path.unlink()
            break
        except (PermissionError, OSError):
            if attempt < max_attempts - 1:
                time.sleep(1)


@pytest.fixture(scope="session", autouse=True)
def initialize_db(request):
    db.create_db_and_tables(db.engine)
    request.addfinalizer(remove_db)
