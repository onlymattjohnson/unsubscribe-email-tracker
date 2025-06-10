import base64
from fastapi.testclient import TestClient

# Path fix might be needed
import sys, os
sys.path.insert(0, os.path.abspath(os.path.join(os.path.dirname(__file__), '..')))

from app.main import app
from app.core.config import settings

client = TestClient(app)

def get_basic_auth_headers(username, password):
    creds = f"{username}:{password}"
    return {"Authorization": f"Basic {base64.b64encode(creds.encode()).decode('ascii')}"}


def test_public_root_endpoint():
    response = client.get("/")
    assert response.status_code == 200

# --- API Auth Tests (/api/v1/...) ---

def test_api_protected_endpoint_success():
    headers = {"Authorization": f"Bearer {settings.API_TOKEN}"}
    response = client.get("/api/v1/test/protected", headers=headers)
    assert response.status_code == 200
    assert response.json()["endpoint_type"] == "api"

def test_api_protected_endpoint_no_token():
    response = client.get("/api/v1/test/protected")
    assert response.status_code == 401
    assert "Not authenticated" in response.json()["detail"]

def test_api_protected_endpoint_wrong_token():
    headers = {"Authorization": "Bearer wrong-token"}
    response = client.get("/api/v1/test/protected", headers=headers)
    assert response.status_code == 401
    assert "Invalid or expired token" in response.json()["detail"]

def test_api_protected_endpoint_with_basic_auth():
    headers = get_basic_auth_headers("user", "pass")
    response = client.get("/api/v1/test/protected", headers=headers)
    assert response.status_code == 401 # Should fail, expects Bearer

# --- Web UI Auth Tests (/web/...) ---

def test_web_protected_endpoint_success():
    headers = get_basic_auth_headers(settings.BASIC_AUTH_USERNAME, settings.BASIC_AUTH_PASSWORD)
    response = client.get("/web/test/protected", headers=headers)
    assert response.status_code == 200
    assert "Authenticated Web UI Endpoint" in response.text

def test_web_protected_endpoint_no_auth():
    response = client.get("/web/test/protected")
    assert response.status_code == 401
    assert response.headers["www-authenticate"] == 'Basic realm="Web UI"'

def test_web_protected_endpoint_wrong_password():
    headers = get_basic_auth_headers(settings.BASIC_AUTH_USERNAME, "wrong-password")
    response = client.get("/web/test/protected", headers=headers)
    assert response.status_code == 401

def test_web_protected_endpoint_with_api_token():
    headers = {"Authorization": f"Bearer {settings.API_TOKEN}"}
    response = client.get("/web/test/protected", headers=headers)
    assert response.status_code == 401 # Should fail, expects Basic