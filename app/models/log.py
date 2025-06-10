from sqlalchemy import Column, Integer, String, TIMESTAMP, text
from sqlalchemy import JSON
from sqlalchemy.sql import func
from app.core.database import Base

class Log(Base):
    __tablename__ = "logs"

    id = Column(Integer, primary_key=True, index=True)
    timestamp = Column(
        TIMESTAMP(timezone=True), nullable=False, server_default=func.now(), index=True
    )
    source_app = Column(String, nullable=False)
    log_level = Column(String, nullable=False)
    message = Column(String, nullable=False)
    details_json = Column(JSON, nullable=True)
    inserted_by = Column(String, nullable=True)