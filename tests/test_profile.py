from fastapi.testclient import TestClient


def test_profile(api_client_authenticated: TestClient) -> None:
    response = api_client_authenticated.get("/profile")
    assert response.status_code == 200
    result = response.json()
    assert "admin" in result["username"]


def test_profile_no_auth(api_client: TestClient) -> None:
    response = api_client.get("/profile")
    assert response.status_code == 401
