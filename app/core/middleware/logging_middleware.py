import logging
import time
import uuid
from typing import Callable

from starlette.middleware.base import BaseHTTPMiddleware
from starlette.requests import Request
from starlette.responses import Response

from app.core.request_context import request_id_cv

logger = logging.getLogger(__name__)

class LoggingMiddleware(BaseHTTPMiddleware):
    async def dispatch(self, request: Request, call_next: Callable) -> Response:
        request_id = str(uuid.uuid4())
        request_id_cv.set(request_id)
        
        start_time = time.time()
        
        logger.info(
            "Request started",
            extra={"method": request.method, "path": request.url.path}
        )
        
        try:
            response = await call_next(request)
            process_time = time.time() - start_time
            
            response.headers["X-Request-ID"] = request_id
            logger.info(
                "Request finished",
                extra={
                    "method": request.method,
                    "path": request.url.path,
                    "status_code": response.status_code,
                    "process_time_ms": round(process_time * 1000, 2),
                },
            )
            return response
        except Exception as e:
            logger.exception(
                "Unhandled exception",
                extra={"method": request.method, "path": request.url.path}
            )
            raise e