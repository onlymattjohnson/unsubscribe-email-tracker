from datetime import datetime
from typing import Iterable, Optional
from sqlalchemy.orm import Session
from sqlalchemy import or_

from app.models.unsubscribed_email import UnsubscribedEmail
from app.schemas.unsubscribed_email import UnsubscribedEmailCreate

def create_unsubscribed_email(db: Session, *, email_in: UnsubscribedEmailCreate) -> UnsubscribedEmail:
    """
    Creates a new unsubscribed email record in the database.
    """
    db_obj = UnsubscribedEmail(
        sender_name=email_in.sender_name,
        sender_email=email_in.sender_email,
        unsub_method=email_in.unsub_method,
    )
    db.add(db_obj)
    db.commit()
    db.refresh(db_obj)
    return db_obj

def get_unsubscribed_emails(
    db: Session,
    *,
    limit: int,
    offset: int,
    unsub_method: Optional[str] = None,
    search: Optional[str] = None,
    date_from: Optional[datetime] = None,
    date_to: Optional[datetime] = None,
) -> list[UnsubscribedEmail]:
    """
    Retrieves a filtered list of unsubscribed emails with pagination.
    """
    query = db.query(UnsubscribedEmail)

    if unsub_method:
        query = query.filter(UnsubscribedEmail.unsub_method == unsub_method)
    
    if search:
        search_term = f"%{search}%"
        query = query.filter(
            or_(
                UnsubscribedEmail.sender_name.ilike(search_term),
                UnsubscribedEmail.sender_email.ilike(search_term),
            )
        )

    if date_from:
        query = query.filter(UnsubscribedEmail.inserted_at >= date_from)

    if date_to:
        query = query.filter(UnsubscribedEmail.inserted_at <= date_to)

    return (
        query.order_by(UnsubscribedEmail.inserted_at.desc(), UnsubscribedEmail.id.desc())
        .offset(offset)
        .limit(limit)
        .all()
    )


def count_unsubscribed_emails(
    db: Session,
    *,
    unsub_method: Optional[str] = None,
    search: Optional[str] = None,
    date_from: Optional[datetime] = None,
    date_to: Optional[datetime] = None,
) -> int:
    """
    Counts the total number of filtered unsubscribed email records.
    """
    query = db.query(UnsubscribedEmail)

    if unsub_method:
        query = query.filter(UnsubscribedEmail.unsub_method == unsub_method)
    
    if search:
        search_term = f"%{search}%"
        query = query.filter(
            or_(
                UnsubscribedEmail.sender_name.ilike(search_term),
                UnsubscribedEmail.sender_email.ilike(search_term),
            )
        )

    if date_from:
        query = query.filter(UnsubscribedEmail.inserted_at >= date_from)

    if date_to:
        query = query.filter(UnsubscribedEmail.inserted_at <= date_to)

    return query.count()

def get_all_unsubscribed_emails(
    db: Session,
    *,
    unsub_method: Optional[str] = None,
    search: Optional[str] = None,
    date_from: Optional[datetime] = None,
    date_to: Optional[datetime] = None,
) -> Iterable[UnsubscribedEmail]:
    """
    Retrieves all filtered unsubscribed emails using a generator.
    """
    query = db.query(UnsubscribedEmail)

    if unsub_method:
        query = query.filter(UnsubscribedEmail.unsub_method == unsub_method)
    
    if search:
        search_term = f"%{search}%"
        query = query.filter(
            or_(
                UnsubscribedEmail.sender_name.ilike(search_term),
                UnsubscribedEmail.sender_email.ilike(search_term),
            )
        )

    if date_from:
        query = query.filter(UnsubscribedEmail.inserted_at >= date_from)

    if date_to:
        query = query.filter(UnsubscribedEmail.inserted_at <= date_to)

    # Use yield_per for memory-efficient iteration
    yield from query.order_by(UnsubscribedEmail.inserted_at.asc()).yield_per(100)