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
    data_iterator = crud.get_all_unsubscribed_emails(
        db=db, unsub_method=unsub_method, search=search,
        date_from=date_from, date_to=date_to
    )

    if format == "csv":
        return generate_csv_stream(data_iterator)
    
    if format == "json":
        # Convert iterator to list of dicts for JSON response
        results = [
            UnsubscribedEmailResponse.model_validate(item).model_dump()
            for item in data_iterator
        ]
        return generate_json_response(results)