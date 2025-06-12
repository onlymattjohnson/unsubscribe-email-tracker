from datetime import datetime
from typing import Literal, Optional
from fastapi import APIRouter, Depends, Query
from sqlalchemy.orm import Session

from app.core import get_db
from app.core.security import require_api_auth
from app.core.export import generate_csv_stream, generate_json_response
from app.crud import unsubscribed_email as crud
from app.schemas.unsubscribed_email import UnsubscribedEmailResponse

router = APIRouter()

@router.get("/export")
async def export_unsubscribed_email_entries(
    *,
    db: Session = Depends(get_db),
    format: Literal["csv", "json"] = Query("csv"),
    # Filter params (same as list endpoint)
    unsub_method: Optional[Literal["direct_link", "isp_level"]] = Query(None),
    search: Optional[str] = Query(None, min_length=1, max_length=100),
    date_from: Optional[datetime] = Query(None),
    date_to: Optional[datetime] = Query(None),
    token: str = Depends(require_api_auth)
):
    """
    Export filtered unsubscribed email records as a CSV or JSON file.
    """
    # Use the existing paginated GET function with a high limit to get all records.
    # This is a pragmatic simplification for non-massive datasets.
    all_items = crud.get_unsubscribed_emails(
        db=db, 
        limit=1_000_000, # A very large number to act as "no limit"
        offset=0, 
        unsub_method=unsub_method,
        search=search, 
        date_from=date_from, 
        date_to=date_to
    )

    results = [
        UnsubscribedEmailResponse.model_validate(item).model_dump(mode="json")
        for item in all_items
    ]

    if format == "csv":
        # Pass the concrete list to the generator
        return generate_csv_stream(results)
    
    if format == "json":
        return generate_json_response(results)
    
    