from fastapi import Request
from fastapi.responses import JSONResponse

from app.core.logging import log_event


class DatabaseConnectionError(Exception):
    """Custom exception for database connection issues."""

    pass


class AuthenticationError(Exception):
    """Custom exception for authentication failures."""

    pass


class ValidationError(Exception):
    """Custom exception for validation errors."""

    pass


async def db_connection_exception_handler(
    request: Request, exc: DatabaseConnectionError
):
    await log_event(
        source_app="api",
        log_level="CRITICAL",
        message="Database connection failed.",
        details_json={"error": str(exc), "url": str(request.url)},
    )
    return JSONResponse(
        status_code=503,
        content={"detail": "Service unavailable due to a database connection error."},
    )


async def auth_exception_handler(request: Request, exc: AuthenticationError):
    return JSONResponse(
        status_code=401,
        content={"detail": str(exc)},
    )
