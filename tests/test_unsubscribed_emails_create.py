from fastapi.testclient import TestClient
import pytest

# Path fix might be needed
import sys, os

sys.path.insert(0, os.path.abspath(os.path.join(os.path.dirname(__file__), "..")))

from app.main import app
from app.core.config import settings
from app.core.logging import log_event

client = TestClient(app)
API_URL = "/api/v1/unsubscribed_emails/"
AUTH_HEADERS = {"Authorization": f"Bearer {settings.API_TOKEN}"}

VALID_PAYLOAD = {
    "sender_name": "Test Newsletter",
    "sender_email": "newsletter@example.com",
    "unsub_method": "direct_link",
}


def test_create_success():
    response = client.post(API_URL, headers=AUTH_HEADERS, json=VALID_PAYLOAD)
    assert response.status_code == 201
    data = response.json()
    assert data["sender_name"] == VALID_PAYLOAD["sender_name"]
    assert data["unsub_method"] == "direct_link"
    assert "id" in data
    assert "inserted_at" in data


def test_create_no_auth():
    response = client.post(API_URL, json=VALID_PAYLOAD)
    assert response.status_code == 401


def test_create_invalid_email():
    payload = VALID_PAYLOAD.copy()
    payload["sender_email"] = "not-an-email"
    response = client.post(API_URL, headers=AUTH_HEADERS, json=payload)
    assert response.status_code == 422  # Unprocessable Entity
    assert "value is not a valid email address" in response.text


def test_create_invalid_unsub_method():
    payload = VALID_PAYLOAD.copy()
    payload["unsub_method"] = "telepathy"
    response = client.post(API_URL, headers=AUTH_HEADERS, json=payload)
    assert response.status_code == 422
    # Use the new Pydantic v2 error message
    assert "Input should be 'direct_link' or 'isp_level'" in response.text


def test_create_missing_sender_name():
    payload = VALID_PAYLOAD.copy()
    del payload["sender_name"]
    response = client.post(API_URL, headers=AUTH_HEADERS, json=payload)
    assert response.status_code == 422
    assert "missing" in response.text


@pytest.mark.asyncio
async def test_creation_is_logged(mocker):
    # Mock the log_event function
    mock_logger = mocker.patch("app.api.v1.endpoints.unsubscribed_emails.log_event")

    # Make a successful request
    client.post(API_URL, headers=AUTH_HEADERS, json=VALID_PAYLOAD)

    # Assert that the logger was called
    mock_logger.assert_awaited_once()
    call_args = mock_logger.call_args[1]
    assert call_args["log_level"] == "INFO"
    assert call_args["message"] == "Unsubscribed email record created."
    assert "created_id" in call_args["details_json"]
