from fastapi import APIRouter, Depends
from sqlalchemy.orm import Session

from app.core.database import get_db
from app.core.exceptions import DatabaseConnectionError

# Apply the dependency to all routes in this router
router = APIRouter()

@router.get("/test/protected")
async def test_protected_endpoint():
    """An endpoint that requires API token authentication."""
    return {"message": "authenticated", "endpoint_type": "api"}

@router.get("/health")
async def health_check(db: Session = Depends(get_db)):
    """Health check endpoint to verify service and database connectivity."""
    try:
        db.execute("SELECT 1")
        return {"status": "healthy", "database": "connected"}
    except Exception as e:
        raise DatabaseConnectionError(f"Health check failed: {e}")