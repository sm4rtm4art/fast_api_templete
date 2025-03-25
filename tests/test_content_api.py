import pytest
from fastapi.testclient import TestClient


@pytest.mark.skip(reason="Content API not fully implemented yet")
def test_content_create(api_client_authenticated: TestClient) -> None:
    """Test creating content."""
    response = api_client_authenticated.post(
        "/content/",
        json={
            "title": "hello test",
            "text": "this is just a test",
            "published": True,
            "tags": ["test", "hello"],
        },
    )
    assert response.status_code == 200
    result = response.json()
    assert result["slug"] == "hello-test"


@pytest.mark.skip(reason="Content API not fully implemented yet")
def test_content_list(api_client_authenticated: TestClient) -> None:
    """Test listing content."""
    response = api_client_authenticated.get("/content/")
    assert response.status_code == 200
    result = response.json()
    assert result[0]["slug"] == "hello-test"
