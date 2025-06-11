from datetime import datetime
from typing import List, Literal

from pydantic import BaseModel, EmailStr, Field, ConfigDict

# Schema for creating an entry (input)
class UnsubscribedEmailCreate(BaseModel):
    sender_name: str = Field(..., min_length=1, max_length=255)
    sender_email: EmailStr
    unsub_method: Literal["direct_link", "isp_level"]

# Schema for reading an entry (output)
class UnsubscribedEmailResponse(BaseModel):
    id: int
    sender_name: str
    sender_email: EmailStr
    unsub_method: str
    inserted_at: datetime

    model_config = ConfigDict(from_attributes=True)

class UnsubscribedEmailList(BaseModel):
    items: List[UnsubscribedEmailResponse]
    total: int
    limit: int
    offset: int