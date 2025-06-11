from fastapi import APIRouter, Depends
from .endpoints import logging as logging_router
from .endpoints import unsubscribed_emails

router = APIRouter()

# Include the unsubscribed_emails endpoint router
router.include_router(
    unsubscribed_emails.router, 
    prefix="/unsubscribed_emails", 
    tags=["Unsubscribed Emails"]
)

# Include other endpoint groups
router.include_router(logging_router.router, prefix="/logs", tags=["Logging"])

# Add a simple protected endpoint for testing purposes
@router.get("/test/protected")
async def test_protected_endpoint():
    """An endpoint that requires API token authentication."""
    return {"message": "authenticated", "endpoint_type": "api"}