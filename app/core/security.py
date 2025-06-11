import base64
import secrets
from typing import Callable

from fastapi import Depends
from starlette.middleware.base import BaseHTTPMiddleware
from starlette.requests import Request
from starlette.responses import Response, JSONResponse
from starlette import status

from app.api.deps import verify_token
from app.core.config import settings

# --- API Authentication ---
def require_api_auth(token: str = Depends(verify_token)):
    """A simple wrapper dependency for API authentication."""
    return token


# --- Web UI Basic Authentication ---
def verify_basic_auth(auth_header: str) -> bool:
    """Verifies Basic Authentication credentials."""
    try:
        scheme, credentials = auth_header.split()
        if scheme.lower() != "basic":
            return False
        
        decoded = base64.b64decode(credentials).decode("ascii")
        username, password = decoded.split(":")

        correct_username = secrets.compare_digest(username, settings.BASIC_AUTH_USERNAME)
        correct_password = secrets.compare_digest(password, settings.BASIC_AUTH_PASSWORD)
        return correct_username and correct_password
    except Exception:
        return False


class BasicAuthMiddleware(BaseHTTPMiddleware):
    async def dispatch(self, request: Request, call_next: Callable) -> Response:
        if not request.url.path.startswith("/web/"):
            return await call_next(request)

        auth_header = request.headers.get("Authorization")
        if not auth_header or not verify_basic_auth(auth_header):
            response = JSONResponse(
                status_code=status.HTTP_401_UNAUTHORIZED,
                content={"detail": "Not authorized"},
                headers={"WWW-Authenticate": 'Basic realm="Web UI"'},
            )
            return response
        
        return await call_next(request)