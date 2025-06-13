import logging
import pytest
from unittest.mock import AsyncMock

# Note: The path fix from before might be needed here too
import sys, os

sys.path.insert(0, os.path.abspath(os.path.join(os.path.dirname(__file__), "..")))

from app.core.logging import log_event
from app.models import Log


@pytest.mark.asyncio
async def test_log_to_database_success(db_session, mocker):
    """Test that a log is successfully written to the database."""
    # Mock SessionLocal to return the test session
    mocker.patch("app.core.logging.SessionLocal", return_value=db_session)

    await log_event(
        source_app="test_suite",
        log_level="INFO",
        message="Successful DB log.",
        details_json={"test_id": 1},
    )

    log = db_session.query(Log).first()
    assert log is not None
    assert log.source_app == "test_suite"
    assert log.message == "Successful DB log."
    assert log.details_json["test_id"] == 1


@pytest.mark.asyncio
async def test_log_fallback_to_structured_log(mocker, caplog):
    """Test that structured logs are created when the database fails."""
    mocker.patch(
        "app.core.logging.SessionLocal", side_effect=Exception("DB connection failed")
    )
    mock_discord = mocker.patch(
        "app.core.logging._send_discord_alert", new_callable=AsyncMock
    )

    with caplog.at_level(logging.ERROR):
        log_id = await log_event(
            source_app="fallback_test",
            log_level="ERROR",
            message="This should be captured.",
        )

    # --- Assertions ---
    assert log_id is None  # ID should be None on failure
    mock_discord.assert_awaited_once()

    # Inspect the captured LogRecord object directly
    assert len(caplog.records) == 1
    record = caplog.records[0]

    assert record.levelname == "ERROR"
    assert "Database logging failed" in record.message

    # Check the structured 'extra' data that was logged
    assert hasattr(record, "original_log")
    assert record.original_log["source_app"] == "fallback_test"
    assert record.original_log["message"] == "This should be captured."


@pytest.mark.asyncio
async def test_log_event_never_raises(mocker):
    """Test that the main log_event function never raises an exception."""
    # 1. Simulate database failure by mocking SessionLocal
    mocker.patch("app.core.logging.SessionLocal", side_effect=Exception("DB is down"))

    # 2. Simulate structured logger failure
    mocker.patch(
        "app.core.logging.logger.error", side_effect=Exception("Logger is broken")
    )

    # 3. Simulate Discord alert failure
    mocker.patch(
        "app.core.logging._send_discord_alert", side_effect=Exception("Discord is down")
    )

    try:
        await log_event("test_suite", "CRITICAL", "Everything is failing")
    except Exception as e:
        pytest.fail(f"log_event raised an exception unexpectedly: {e}")
