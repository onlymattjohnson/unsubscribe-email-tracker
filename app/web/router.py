from fastapi import APIRouter
from fastapi.responses import HTMLResponse

router = APIRouter()

@router.get("/test/protected")
async def test_web_protected_endpoint():
    """An endpoint protected by Basic Auth middleware."""
    content = "<h1>Authenticated Web UI Endpoint</h1>"
    return HTMLResponse(content=content)