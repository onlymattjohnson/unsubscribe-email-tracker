import asyncio
import time
from math import ceil
from typing import List, Dict, Optional, Callable

from starlette.middleware.base import BaseHTTPMiddleware
from starlette.requests import Request
from starlette.responses import Response, JSONResponse
from starlette import status

from app.core.config import settings
from app.core.logging import log_event


class RateLimiter:
    """An async-safe, in-memory, sliding window rate limiter."""

    def __init__(self):
        self._requests: Dict[str, List[float]] = {}
        self._lock = asyncio.Lock()

    async def is_rate_limited(
        self, identifier: str, limit: int, window: int
    ) -> Optional[int]:
        """
        Checks if an identifier has exceeded the rate limit.

        Returns:
            - None if not rate-limited.
            - An integer representing seconds to wait if rate-limited.
        """
        now = time.time()
        async with self._lock:
            timestamps = self._requests.get(identifier, [])

            # Slide the window: filter out timestamps older than the window
            relevant_timestamps = [t for t in timestamps if now - t <= window]

            if len(relevant_timestamps) >= limit:
                oldest_request_time = relevant_timestamps[0]
                retry_after = int(ceil(window - (now - oldest_request_time)))
                return retry_after

            relevant_timestamps.append(now)
            self._requests[identifier] = relevant_timestamps
            return None

    async def cleanup(self):
        """Removes old identifiers and timestamps to prevent memory leaks."""
        now = time.time()
        window = settings.RATE_LIMIT_TIMESCALE_SECONDS
        async with self._lock:
            # Using list(keys()) to avoid issues with modifying dict during iteration
            for identifier in list(self._requests.keys()):
                timestamps = self._requests[identifier]
                self._requests[identifier] = [
                    t for t in timestamps if now - t <= window
                ]
                if not self._requests[identifier]:
                    del self._requests[identifier]
        await log_event("rate_limiter", "INFO", "Cleanup task completed.")


async def cleanup_task(limiter: RateLimiter, interval_seconds: int = 300):
    """Background task to periodically run the rate limiter cleanup."""
    while True:
        await asyncio.sleep(interval_seconds)
        await limiter.cleanup()


class RateLimitMiddleware(BaseHTTPMiddleware):
    EXCLUDED_PATHS = ["/docs", "/openapi.json"]

    def __init__(self, app, limiter: RateLimiter):
        super().__init__(app)
        self.limiter = limiter

    async def dispatch(self, request: Request, call_next: Callable) -> Response:
        if not settings.RATE_LIMIT_ENABLED or any(
            request.url.path.startswith(p) for p in self.EXCLUDED_PATHS
        ):
            return await call_next(request)

        # Identify by token if present (authenticated), otherwise by IP (anonymous)
        auth_header = request.headers.get("Authorization")
        is_authenticated = auth_header and auth_header.lower().startswith("bearer ")

        if is_authenticated:
            identifier = auth_header.split(" ")[1]
            limit = settings.RATE_LIMIT_AUTH_REQUESTS
        else:
            identifier = request.client.host
            limit = settings.RATE_LIMIT_REQUESTS

        window = settings.RATE_LIMIT_TIMESCALE_SECONDS

        retry_after = await self.limiter.is_rate_limited(identifier, limit, window)

        if retry_after is not None:
            await log_event(
                "rate_limiter",
                "WARNING",
                "Rate limit exceeded",
                details_json={"identifier": identifier, "path": request.url.path},
            )
            return JSONResponse(
                status_code=status.HTTP_429_TOO_MANY_REQUESTS,
                content={
                    "detail": f"Too many requests. Try again in {retry_after} seconds."
                },
                headers={"Retry-After": str(retry_after)},
            )

        return await call_next(request)
