import math
from typing import Optional, Literal, Union
from urllib.parse import urlencode

from fastapi import APIRouter, Depends, Request, Query
from fastapi.responses import HTMLResponse, RedirectResponse
from fastapi.templating import Jinja2Templates

# We need the dependency from the new deps file
from app.web.deps import get_templates

from app.crud import unsubscribed_email as crud
from app.core import get_db
from sqlalchemy.orm import Session

from . import export as export_routes

router = APIRouter()
router.include_router(export_routes.router)


def build_query_params(base_params: dict, new_params: dict) -> str:
    """Helper to build query strings, preserving existing filters."""
    updated_params = base_params.copy()
    updated_params.update(new_params)
    # Filter out None values before encoding
    return urlencode({k: v for k, v in updated_params.items() if v is not None})


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
    page: int = Query(1, ge=1),
    search: Optional[str] = Query(None, min_length=1, max_length=100),
    unsub_method: Optional[
        Union[Literal["direct_link", "isp_level"], Literal[""]]
    ] = Query(None),
):
    """Displays the main page for unsubscribed emails with pagination and filters."""
    offset = (page - 1) * ITEMS_PER_PAGE

    final_search = None if search == "" else search
    final_unsub_method = None if unsub_method == "" else unsub_method

    items = crud.get_unsubscribed_emails(
        db=db,
        limit=ITEMS_PER_PAGE,
        offset=offset,
        search=final_search,
        unsub_method=final_unsub_method,
    )
    total_count = crud.count_unsubscribed_emails(
        db=db, search=final_search, unsub_method=final_unsub_method
    )

    total_pages = math.ceil(total_count / ITEMS_PER_PAGE) if total_count > 0 else 1

    current_filters = {"search": final_search, "unsub_method": final_unsub_method}

    # Override the href in the pagination template by passing it in the context
    def pagination_url(page_num: int) -> str:
        # Pass the original query params to keep them in the URL
        # but the logic uses the sanitized final_ ones
        return f"?{build_query_params({'search': search, 'unsub_method': unsub_method}, {'page': page_num})}"

    context = {
        "request": request,
        "items": items,
        "total_count": total_count,
        "current_page": page,
        "total_pages": total_pages,
        "current_filters": current_filters,
        "pagination_url": pagination_url,
        "export_url_csv": f"/web/export?{build_query_params({'search': search, 'unsub_method': unsub_method}, {'format': 'csv'})}",
        "export_url_json": f"/web/export?{build_query_params({'search': search, 'unsub_method': unsub_method}, {'format': 'json'})}",
    }
    return templates.TemplateResponse(
        request=request, name="unsubscribed_list.html", context=context
    )
