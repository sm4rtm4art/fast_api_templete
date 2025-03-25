from fastapi.testclient import TestClient


def test_profile(api_client_authenticated: TestClient) -> None:
    """Test the profile endpoint (/me)."""
    response = api_client_authenticated.get("/me")
    assert response.status_code == 200
    result = response.json()
    assert "admin" in result["username"]


def test_profile_no_auth(api_client: TestClient) -> None:
    """Test the profile endpoint without authentication."""
    response = api_client.get("/me")
    assert response.status_code == 401
