import logging
from fastapi.testclient import TestClient
from unittest.mock import patch, AsyncMock

# Path fix if needed
import sys, os
sys.path.insert(0, os.path.abspath(os.path.join(os.path.dirname(__file__), '..')))

from app.main import app
from app.core.config import settings

client = TestClient(app)
auth_headers = {"Authorization": f"Bearer {settings.API_TOKEN}"}

def test_post_log_success():
    log_data = {
        "source_app": "test_suite",
        "log_level": "INFO",
        "message": "Testing log POST endpoint"
    }
    response = client.post("/api/v1/logs", json=log_data, headers=auth_headers)
    assert response.status_code == 201
    data = response.json()
    assert data["status"] == "logged"
    assert isinstance(data["log_id"], int)

@patch("app.core.logging.SessionLocal")
@patch("app.core.logging._send_discord_alert", new_callable=AsyncMock)
def test_post_log_fallback(mock_discord, mock_session_local):
    # Simulate DB failure
    mock_session_local.side_effect = Exception("DB is down")
    
    log_data = {"source_app": "test_suite", "log_level": "ERROR", "message": "Testing fallback"}
    response = client.post("/api/v1/logs", json=log_data, headers=auth_headers)
    
    assert response.status_code == 201
    data = response.json()
    assert data["status"] == "logged"
    assert data["log_id"] is None # Should be None on failure
    mock_discord.assert_awaited_once()

def test_get_logs(db_session): # Using a fixture that provides a real session
    # Create a test log first
    client.post("/api/v1/logs", json={"source_app": "get_test", "log_level": "DEBUG", "message": "log 1"}, headers=auth_headers)
    
    response = client.get("/api/v1/logs?source_app=get_test", headers=auth_headers)
    assert response.status_code == 200
    data = response.json()
    assert data["total"] >= 1
    assert data["data"][0]["source_app"] == "get_test"

def test_logging_middleware(caplog):
    with caplog.at_level(logging.INFO):
        response = client.get("/") # Request a simple endpoint
    
    # Check for the two logs from the middleware
    assert "Request started" in caplog.text
    assert "Request finished" in caplog.text
    
    # Check for request_id in headers
    assert "x-request-id" in response.headers