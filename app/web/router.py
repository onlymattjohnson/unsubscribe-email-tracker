import math
from fastapi import APIRouter, Depends, Request, Query
from fastapi.responses import HTMLResponse, RedirectResponse
from fastapi.templating import Jinja2Templates

# We need the dependency from the new deps file
from app.web.deps import get_templates

from app.crud import unsubscribed_email as crud
from app.core import get_db
from sqlalchemy.orm import Session

router = APIRouter()

# --- NEW ROUTES ---
@router.get("/")
async def web_root():
    """Redirects the root of the web UI to the main list page."""
    return RedirectResponse(url="/web/unsubscribed")

# --- EXISTING TEST ROUTE ---
@router.get("/test/protected")
async def test_web_protected_endpoint():
    """An endpoint protected by Basic Auth middleware."""
    content = "<h1>Authenticated Web UI Endpoint</h1>"
    return HTMLResponse(content=content)

ITEMS_PER_PAGE = 20

@router.get("/unsubscribed")
async def list_unsubscribed(
    request: Request,
    db: Session = Depends(get_db),
    templates: Jinja2Templates = Depends(get_templates),
    page: int = Query(1, ge=1)
):
    """Displays the main page for unsubscribed emails with pagination."""
    offset = (page - 1) * ITEMS_PER_PAGE
    
    items = crud.get_unsubscribed_emails(db=db, limit=ITEMS_PER_PAGE, offset=offset)
    total_count = crud.count_unsubscribed_emails(db=db)
    
    total_pages = math.ceil(total_count / ITEMS_PER_PAGE) if total_count > 0 else 1

    context = {
        "request": request,
        "items": items,
        "total_count": total_count,
        "current_page": page,
        "total_pages": total_pages
    }
    return templates.TemplateResponse(request=request, name="unsubscribed_list.html", context=context)