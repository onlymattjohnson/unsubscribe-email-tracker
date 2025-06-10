from contextvars import ContextVar
from typing import Optional

# Context variable to hold the request ID
request_id_cv: ContextVar[Optional[str]] = ContextVar("request_id", default=None)