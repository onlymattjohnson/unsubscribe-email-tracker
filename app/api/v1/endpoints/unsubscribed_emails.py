from fastapi import APIRouter, Depends, status
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