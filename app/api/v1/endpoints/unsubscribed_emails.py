from datetime import datetime
from typing import Literal, Optional
from fastapi import APIRouter, Depends, status, Query
from sqlalchemy.orm import Session

from app.core import get_db, log_event
from app.core.security import require_api_auth
from app.crud import unsubscribed_email as crud
from app.schemas import unsubscribed_email as schemas

router = APIRouter()

@router.post(
    "/",
    response_model=schemas.UnsubscribedEmailResponse,
    status_code=status.HTTP_201_CREATED,
)
async def create_unsubscribed_email_entry(
    *,
    db: Session = Depends(get_db),
    email_in: schemas.UnsubscribedEmailCreate,
    token: str = Depends(require_api_auth),
):
    """
    Create a new record for an unsubscribed email.
    """
    created_email = crud.create_unsubscribed_email(db=db, email_in=email_in)
    
    await log_event(
        source_app="api",
        log_level="INFO",
        message="Unsubscribed email record created.",
        details_json={
            "created_id": created_email.id,
            "sender_email": created_email.sender_email,
        },
        inserted_by="api_token" # Don't log the token itself
    )
    
    return created_email

@router.get(
    "/",
    response_model=schemas.UnsubscribedEmailList,
)
async def list_unsubscribed_email_entries(
    *,
    db: Session = Depends(get_db),
    # Pagination params
    limit: int = Query(10, ge=1, le=100),
    offset: int = Query(0, ge=0),
    # Filter params
    unsub_method: Optional[Literal["direct_link", "isp_level"]] = Query(None),
    search: Optional[str] = Query(None, min_length=1, max_length=100),
    date_from: Optional[datetime] = Query(None, description="ISO 8601 format: YYYY-MM-DDTHH:MM:SS"),
    date_to: Optional[datetime] = Query(None, description="ISO 8601 format: YYYY-MM-DDTHH:MM:SS"),
    # Auth
    token: str = Depends(require_api_auth),
):
    """
    Retrieve a paginated and filtered list of unsubscribed email records.
    """
    items = crud.get_unsubscribed_emails(
        db=db, limit=limit, offset=offset, unsub_method=unsub_method,
        search=search, date_from=date_from, date_to=date_to
    )
    total = crud.count_unsubscribed_emails(
        db=db, unsub_method=unsub_method, search=search,
        date_from=date_from, date_to=date_to
    )


    
    return schemas.UnsubscribedEmailList(
        items=items, total=total, limit=limit, offset=offset
    )