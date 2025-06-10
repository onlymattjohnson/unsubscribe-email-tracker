from sqlalchemy import Column, Integer, String, TIMESTAMP, CheckConstraint
from sqlalchemy.sql import func
from app.core.database import Base

class UnsubscribedEmail(Base):
    __tablename__ = "unsubscribed_emails"

    id = Column(Integer, primary_key=True, index=True)
    sender_name = Column(String, nullable=False)
    sender_email = Column(String, nullable=False, index=True)
    unsub_method = Column(String, nullable=False)
    inserted_at = Column(
        TIMESTAMP(timezone=True), nullable=False, server_default=func.now()
    )

    __table_args__ = (
        CheckConstraint(
            "unsub_method IN ('direct_link', 'isp_level')", name="unsub_method_check"
        ),
    )