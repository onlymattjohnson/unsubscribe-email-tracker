from fastapi import APIRouter
from .endpoints import logging as logging_router

router = APIRouter()

# Include other endpoint groups
router.include_router(logging_router.router, prefix="/logs", tags=["Logging"])

# Add a simple protected endpoint for testing purposes
@router.get("/test/protected")
async def test_protected_endpoint():
    """An endpoint that requires API token authentication."""
    return {"message": "authenticated", "endpoint_type": "api"}