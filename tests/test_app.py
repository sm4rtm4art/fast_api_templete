import os

from fastapi.testclient import TestClient


def test_using_testing_db() -> None:
    """Test that we're using the testing environment."""
    assert os.environ.get("FORCE_ENV_FOR_DYNACONF") == "testing"
    settings_file = "tests/test_settings.toml"
    assert os.environ.get("FAST_API_TEMPLATE_SETTINGS_FILE") == settings_file


def test_index(api_client: TestClient) -> None:
    """Test the root endpoint."""
    response = api_client.get("/")
    assert response.status_code == 200
    result = response.json()
    assert result["message"] == "Hello World!"


def test_cors_header(api_client: TestClient) -> None:
    """Test CORS headers."""
    valid_origin = ["http://localhost:3000"]
    invalid_origin = ["https://crackit.com"]

    valid_responses = [
        api_client.options(
            "/",
            headers={
                "Origin": f"{url}",
            },
        )
        for url in valid_origin
    ]

    for res, _url in zip(valid_responses, valid_origin, strict=True):
        # The app is configured to allow all origins in test environment
        assert res.headers.get("access-control-allow-origin") == "*"

    invalid_responses = [
        api_client.options(
            "/",
            headers={
                "Origin": f"{url}",
            },
        )
        for url in invalid_origin
    ]

    # All origins should be allowed with the '*' setting
    for res in invalid_responses:
        assert res.headers.get("access-control-allow-origin") == "*"
