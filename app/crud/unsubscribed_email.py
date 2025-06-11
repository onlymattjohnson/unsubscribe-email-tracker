from sqlalchemy.orm import Session

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

def get_unsubscribed_emails(db: Session, *, limit: int, offset: int) -> list[UnsubscribedEmail]:
    """
    Retrieves a list of unsubscribed emails with pagination.
    """
    return (
        db.query(UnsubscribedEmail)
        .order_by(UnsubscribedEmail.inserted_at.desc())
        .offset(offset)
        .limit(limit)
        .all()
    )

def count_unsubscribed_emails(db: Session) -> int:
    """
    Counts the total number of unsubscribed email records.
    """
    return db.query(UnsubscribedEmail).count()