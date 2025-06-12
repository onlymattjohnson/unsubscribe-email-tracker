from fastapi import APIRouter, Depends, Request
from fastapi.responses import HTMLResponse, RedirectResponse
from fastapi.templating import Jinja2Templates

# We need the dependency from the new deps file
from app.web.deps import get_templates

router = APIRouter()

# --- NEW ROUTES ---
@router.get("/")
async def web_root():
    """Redirects the root of the web UI to the main list page."""
    return RedirectResponse(url="/web/unsubscribed")

@router.get("/unsubscribed")
async def list_unsubscribed(
    request: Request,
    templates: Jinja2Templates = Depends(get_templates)
):
    """Displays the main page for unsubscribed emails (placeholder)."""
    return templates.TemplateResponse(request=request, name="unsubscribed_list.html")


# --- EXISTING TEST ROUTE ---
@router.get("/test/protected")
async def test_web_protected_endpoint():
    """An endpoint protected by Basic Auth middleware."""
    content = "<h1>Authenticated Web UI Endpoint</h1>"
    return HTMLResponse(content=content)