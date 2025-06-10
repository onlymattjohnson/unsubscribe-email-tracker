import json
import pytest
from unittest.mock import AsyncMock

# Note: The path fix from before might be needed here too
import sys, os
sys.path.insert(0, os.path.abspath(os.path.join(os.path.dirname(__file__), '..')))

from app.core.logging import log_event, LOG_FILE_PATH
from app.models import Log

# Use the same db_session fixture from test_models
from .test_models import db_session

@pytest.mark.asyncio
async def test_log_to_database_success(db_session):
    """Test that a log is successfully written to the database."""
    await log_event(
        source_app="test_suite",
        log_level="INFO",
        message="Successful DB log.",
        details_json={"test_id": 1}
    )
    log = db_session.query(Log).first()
    assert log is not None
    assert log.source_app == "test_suite"
    assert log.message == "Successful DB log."
    assert log.details_json["test_id"] == 1

@pytest.mark.asyncio
async def test_log_fallback_to_file(mocker, tmp_path):
    """Test that logs are written to a file when the database fails."""
    # Mock the DB call to raise an error
    mocker.patch("app.core.logging._log_to_database", side_effect=Exception("DB connection failed"))
    # Mock Discord alert so we don't send real alerts during tests
    mock_discord = mocker.patch("app.core.logging._send_discord_alert", new_callable=AsyncMock)

    # Use a temporary log file for this test
    temp_log_file = tmp_path / "test_app.log"
    mocker.patch("app.core.logging.LOG_FILE_PATH", temp_log_file)

    await log_event(
        source_app="fallback_test",
        log_level="ERROR",
        message="This should go to file."
    )

    # Assertions
    assert temp_log_file.exists()
    with open(temp_log_file, "r") as f:
        log_data = json.loads(f.read())
        assert log_data["source_app"] == "fallback_test"
        assert log_data["message"] == "This should go to file."

    # Assert that the Discord alert was also triggered
    mock_discord.assert_awaited_once()

@pytest.mark.asyncio
async def test_log_event_never_raises(mocker):
    """Test that the main log_event function never raises an exception."""
    mocker.patch("app.core.logging._log_to_database", side_effect=Exception("Generic DB Error"))
    mocker.patch("app.core.logging._send_discord_alert", side_effect=Exception("Discord is down"))
    mocker.patch("app.core.logging._log_to_file", side_effect=Exception("Disk is full"))

    try:
        await log_event("test_suite", "CRITICAL", "Everything is failing")
    except Exception as e:
        pytest.fail(f"log_event raised an exception unexpectedly: {e}")