import httpx
from typing import Optional, Literal
from fastapi import APIRouter, Depends, Query, Request
from fastapi.responses import StreamingResponse

from app.core import settings
from app.core.security import verify_basic_auth  # We can reuse this for a simple check

router = APIRouter()


@router.get("/export")
async def web_export(
    request: Request,
    format: Literal["csv", "json"] = Query("csv"),
    # Accept same filters
    unsub_method: Optional[Literal["direct_link", "isp_level"]] = Query(None),
    search: Optional[str] = Query(None, min_length=1, max_length=100),
):
    """
    Acts as an authenticated proxy to the API's export endpoint.
    The Basic Auth middleware will protect this route.
    """
    # Build the API URL with forwarded query parameters
    api_url = f"http://127.0.0.1:8000/api/v1/unsubscribed_emails/export"

    # Forward filters to the API call
    params = {"format": format, "unsub_method": unsub_method, "search": search}
    # Filter out None values
    filtered_params = {k: v for k, v in params.items() if v is not None}

    headers = {"Authorization": f"Bearer {settings.API_TOKEN}"}

    async with httpx.AsyncClient() as client:
        api_response = await client.get(
            api_url, params=filtered_params, headers=headers, timeout=30.0
        )

    # Stream the response from the API back to the user
    return StreamingResponse(
        api_response.iter_bytes(),
        status_code=api_response.status_code,
        headers=api_response.headers,
    )
