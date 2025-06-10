from datetime import datetime
from typing import List, Optional

from fastapi import APIRouter, Depends, Query
from pydantic import BaseModel, ConfigDict 
from sqlalchemy.orm import Session

from app.core.database import get_db
from app.core.logging import log_event, get_logs

router = APIRouter()

class LogCreate(BaseModel):
    source_app: str
    log_level: str
    message: str
    details_json: Optional[dict] = None

class LogResponse(BaseModel):
    id: int
    timestamp: datetime
    source_app: str
    log_level: str
    message: str
    details_json: Optional[dict] = None
    inserted_by: Optional[str] = None

    model_config = ConfigDict(from_attributes=True)

class PaginatedLogResponse(BaseModel):
    total: int
    limit: int
    offset: int
    data: List[LogResponse]


@router.post("", status_code=201, response_model=dict)
async def create_log_entry(log_in: LogCreate):
    log_id = await log_event(
        source_app=log_in.source_app,
        log_level=log_in.log_level,
        message=log_in.message,
        details_json=log_in.details_json,
    )
    return {"status": "logged", "log_id": log_id}

@router.get("", response_model=PaginatedLogResponse)
def read_logs(
    db: Session = Depends(get_db),
    limit: int = Query(100, ge=1, le=1000),
    offset: int = Query(0, ge=0),
    source_app: Optional[str] = None,
    log_level: Optional[str] = None,
):
    logs, total = get_logs(db, limit, offset, source_app, log_level)
    return {
        "total": total,
        "limit": limit,
        "offset": offset,
        "data": logs,
    }