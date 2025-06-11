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