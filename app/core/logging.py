import json
import traceback
from datetime import datetime, timezone
from pathlib import Path
from typing import Optional, Dict, Any


import httpx
from sqlalchemy.orm import Session

from app.core.config import settings
from app.core.database import SessionLocal
from app.models.log import Log

LOG_FILE_PATH = Path("logs/app.log")

async def _log_to_database(
    db: Session,
    source_app: str,
    log_level: str,
    message: str,
    details_json: Optional[Dict[str, Any]] = None,
    inserted_by: Optional[str] = None,
) -> int:
    """Helper to insert a log entry into the database."""
    log_entry = Log(
        source_app=source_app,
        log_level=log_level,
        message=message,
        details_json=details_json,
        inserted_by=inserted_by,
    )
    db.add(log_entry)
    db.commit()
    db.refresh(log_entry)
    return log_entry.id

async def _log_to_file(
    source_app: str,
    log_level: str,
    message: str,
    details_json: Optional[Dict[str, Any]] = None,
    inserted_by: Optional[str] = None,
):
    """Fallback to write log to a local file if DB fails."""
    log_record = {
        "timestamp": datetime.now(timezone.utc).isoformat(),
        "source_app": source_app,
        "log_level": log_level,
        "message": message,
        "details_json": details_json,
        "inserted_by": inserted_by,
    }
    try:
        LOG_FILE_PATH.parent.mkdir(exist_ok=True, parents=True)
        with open(LOG_FILE_PATH, "a") as f:
            f.write(json.dumps(log_record) + "\n")
    except Exception:
        # If file logging also fails, print to stderr as a last resort.
        print(f"CRITICAL: Failed to write log to file: {log_record}")
        traceback.print_exc()

async def _send_discord_alert(original_message: str, error: Exception):
    """Sends an alert to a Discord webhook about a logging failure."""
    if not settings.DISCORD_WEBHOOK_URL:
        return

    message = (
        f"🚨 **Logging System Alert** 🚨\n\n"
        f"**Failed to write log to database.**\n\n"
        f"**Original Message:**\n```\n{original_message}\n```\n\n"
        f"**Error:**\n```\n{error}\n```\n\n"
        f"The log has been written to the local fallback file (`{LOG_FILE_PATH}`)."
    )

    try:
        async with httpx.AsyncClient() as client:
            await client.post(settings.DISCORD_WEBHOOK_URL, json={"content": message})
    except Exception as e:
        print(f"CRITICAL: Failed to send Discord alert: {e}")
        await _log_to_file(
            source_app="logging_system",
            log_level="CRITICAL",
            message="Failed to send Discord alert",
            details_json={"error": str(e)}
        )

async def log_event(
    source_app: str,
    log_level: str,
    message: str,
    details_json: Optional[Dict[str, Any]] = None,
    inserted_by: Optional[str] = None,
):
    """
    Main logging function. Tries to log to DB, falls back to file + alert.
    This function should never raise an exception.
    """
    db = None
    try:
        db = SessionLocal()
        await _log_to_database(
            db, source_app, log_level, message, details_json, inserted_by
        )
    except Exception as db_error:
        print(f"ERROR: Database logging failed. Falling back. Error: {db_error}")
        original_log_message = f"{log_level} | {source_app} | {message}"

        # Fallback 1: Log to file (wrapped in its own try/except)
        try:
            await _log_to_file(
                source_app, log_level, message, details_json, inserted_by
            )
        except Exception as file_error:
            print(f"CRITICAL: Fallback logging to file also failed. Error: {file_error}")

        # Fallback 2: Send alert (wrapped in its own try/except)
        try:
            await _send_discord_alert(original_log_message, db_error)
        except Exception as alert_error:
            print(f"CRITICAL: Fallback Discord alert also failed. Error: {alert_error}")

    finally:
        if db:
            db.close()