import logging
from datetime import datetime, timezone
from typing import Optional, Dict, Any, List, Tuple

import httpx
from sqlalchemy.orm import Session

from app.core.config import settings
from app.core.database import SessionLocal
from app.models.log import Log

logger = logging.getLogger(__name__)


def get_logs(db: Session, limit: int, offset: int, source_app: Optional[str], log_level: Optional[str]) -> Tuple[List[Log], int]:
    """Retrieves a paginated and filtered list of logs from the database."""
    query = db.query(Log)
    if source_app:
        query = query.filter(Log.source_app == source_app)
    if log_level:
        query = query.filter(Log.log_level == log_level)
    
    total = query.count()
    logs = query.order_by(Log.timestamp.desc()).limit(limit).offset(offset).all()
    return logs, total


async def _send_discord_alert(original_message: str, error: Exception):
    """(This function remains the same as before)"""
    # ... (code from previous step)
    if not settings.DISCORD_WEBHOOK_URL:
        return
    # ...


async def log_event(
    source_app: str,
    log_level: str,
    message: str,
    details_json: Optional[Dict[str, Any]] = None,
    inserted_by: Optional[str] = None,
) -> Optional[int]:
    """
    Main logging function. Tries to log to DB, falls back to structured log.
    Returns the log ID if successful, otherwise None. This function should never raise.
    """
    db = None
    try:
        db = SessionLocal()
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
    except Exception as db_error:
        # --- Fallback Logic ---
        try:
            logger.error(
                "Database logging failed. The original log is being captured in standard output.",
                extra={
                    "db_error": str(db_error),
                    "original_log": {
                        "source_app": source_app,
                        "log_level": log_level,
                        "message": message,
                        "details": details_json,
                    },
                },
            )
        except Exception as log_err:
            # Last resort if even the logger fails
            print(f"CRITICAL: Primary DB and structured logging have both failed. Error: {log_err}")

        try:
            original_log_message = f"{log_level} | {source_app} | {message}"
            await _send_discord_alert(original_log_message, db_error)
        except Exception as alert_err:
            print(f"CRITICAL: Discord alert failed after DB logging failure. Error: {alert_err}")

        return None
    finally:
        if db:
            db.close()