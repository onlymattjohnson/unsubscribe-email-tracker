from fastapi import APIRouter

# Note: We no longer need Session, Depends, get_db, etc. here
# because the health check is moving out.

router = APIRouter()

@router.get("/test/protected")
async def test_protected_endpoint():
    """An endpoint that requires API token authentication."""
    return {"message": "authenticated", "endpoint_type": "api"}