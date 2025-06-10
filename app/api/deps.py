from fastapi import Depends, HTTPException, status
from fastapi.security import HTTPBearer, HTTPAuthorizationCredentials

from app.core.config import settings

bearer_scheme = HTTPBearer()

async def get_current_token(
    credentials: HTTPAuthorizationCredentials = Depends(bearer_scheme),
) -> str:
    """Extracts the bearer token from the Authorization header."""
    return credentials.credentials


async def verify_token(token: str = Depends(get_current_token)):
    """
    Dependency that verifies the bearer token against the API_TOKEN in settings.
    Raises HTTPException 401 if the token is invalid.
    """
    if token != settings.API_TOKEN:
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Invalid or expired token",
            headers={"WWW-Authenticate": "Bearer"},
        )
    return token