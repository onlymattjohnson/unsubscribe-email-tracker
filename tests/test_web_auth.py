import base64
from fastapi.testclient import TestClient

from app.core.config import settings


def get_basic_auth_headers(username, password):
    creds = f"{username}:{password}"
    return {
        "Authorization": f"Basic {base64.b64encode(creds.encode()).decode('ascii')}"
    }


def test_web_unauthorized(test_client: TestClient):
    """Test accessing a web route without credentials."""
    response = test_client.get("/web/unsubscribed")
    assert response.status_code == 401
    assert "Authentication Required" in response.text
    assert response.headers["www-authenticate"] == 'Basic realm="Web UI"'


def test_web_invalid_credentials(test_client: TestClient):
    """Test accessing a web route with wrong credentials."""
    headers = get_basic_auth_headers("admin", "wrongpassword")
    response = test_client.get("/web/unsubscribed", headers=headers)
    assert response.status_code == 401
    assert "Authentication Required" in response.text


def test_web_authorized_access(test_client: TestClient):
    """Test successful access with valid credentials."""
    headers = get_basic_auth_headers(
        settings.BASIC_AUTH_USERNAME, settings.BASIC_AUTH_PASSWORD
    )
    response = test_client.get("/web/unsubscribed", headers=headers)
    assert response.status_code == 200
    assert "Unsubscribed Emails</h1>" in response.text


def test_web_root_redirect(test_client: TestClient):
    """Test that the /web/ root redirects correctly when authenticated."""
    headers = get_basic_auth_headers(
        settings.BASIC_AUTH_USERNAME, settings.BASIC_AUTH_PASSWORD
    )
    # The TestClient automatically follows redirects
    response = test_client.get("/web/", headers=headers)
    assert response.status_code == 200
    # Check the final URL after redirect
    assert response.url.path == "/web/unsubscribed"
