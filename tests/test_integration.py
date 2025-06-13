import pytest
import csv
import io
from fastapi.testclient import TestClient
from sqlalchemy.orm import Session
from unittest.mock import AsyncMock

from app.models import UnsubscribedEmail
from app.core.logging import log_event


def test_transaction_rollback_on_failure(test_client: TestClient, db_session: Session, mocker):
    """
    Tests that a database transaction is rolled back if an error occurs
    during an API call, ensuring data integrity.
    """
    initial_count = db_session.query(UnsubscribedEmail).count()

    mocker.patch(
        "app.crud.unsubscribed_email.create_unsubscribed_email",
        side_effect=Exception("Simulated unexpected database error")
    )
    
    payload = {
        "sender_name": "Test Company",
        "sender_email": "test@company.com",
        "unsub_method": "direct_link"
    }
    
    from .test_export import AUTH_HEADERS
    response = test_client.post("/api/v1/unsubscribed_emails/", headers=AUTH_HEADERS, json=payload)
    
    assert response.status_code == 500

    final_count = db_session.query(UnsubscribedEmail).count()
    assert final_count == initial_count


@pytest.mark.asyncio
async def test_successful_api_action_is_logged(test_client: TestClient, mocker):
    """
    Tests that a successful API action correctly calls the logging system.
    """
    mock_logger = mocker.patch("app.api.v1.endpoints.unsubscribed_emails.log_event", new_callable=AsyncMock)
    
    payload = {
        "sender_name": "Logging Test",
        "sender_email": "log@test.com",
        "unsub_method": "direct_link"
    }
    from .test_export import AUTH_HEADERS
    test_client.post("/api/v1/unsubscribed_emails/", headers=AUTH_HEADERS, json=payload)
    
    mock_logger.assert_awaited_once()


@pytest.mark.asyncio
async def test_logging_system_fallback_integration(mocker):
    """
    Tests the integration of the logging system's fallback mechanisms.
    """
    # Mock the database session to simulate a database failure
    mock_session = mocker.MagicMock()
    mock_session.add.side_effect = Exception("DB down")
    mocker.patch("app.core.logging.SessionLocal", return_value=mock_session)
    
    # Mock the standard logger to verify fallback logging
    mock_logger = mocker.patch("app.core.logging.logger")
    
    # Mock Discord alert
    mock_discord_alert = mocker.patch("app.core.logging._send_discord_alert", new_callable=AsyncMock)

    # Call log_event - it should handle the DB error gracefully
    result = await log_event("test_app", "CRITICAL", "This is a test of the fallback system.")

    # Verify the fallback mechanisms were triggered
    assert result is None  # Should return None when DB fails
    
    # Verify logger.error was called for fallback logging
    mock_logger.error.assert_called_once()
    error_call_args = mock_logger.error.call_args
    assert "Database logging failed" in error_call_args[0][0]
    
    # Verify Discord alert was called
    mock_discord_alert.assert_awaited_once()
    discord_call_args = mock_discord_alert.call_args[0]
    assert "CRITICAL | test_app | This is a test of the fallback system." in discord_call_args[0]
    assert isinstance(discord_call_args[1], Exception)


def test_export_with_large_dataset(test_client: TestClient, db_session: Session):
    """
    Tests that the export function correctly handles a dataset larger than
    the default pagination limit.
    """
    records_to_create = [
        UnsubscribedEmail(sender_name=f"Bulk Sender {i}", sender_email=f"bulk{i}@test.com", unsub_method="direct_link")
        for i in range(150)
    ]
    db_session.add_all(records_to_create)
    db_session.commit()

    from .test_export import AUTH_HEADERS
    response = test_client.get("/api/v1/unsubscribed_emails/export?format=csv", headers=AUTH_HEADERS)
    assert response.status_code == 200

    reader = csv.reader(io.StringIO(response.text))
    rows = list(reader)
    
    assert len(rows) == 151