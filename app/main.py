import asyncio, logging
from contextlib import asynccontextmanager
from fastapi import Depends, FastAPI
from fastapi.middleware.cors import CORSMiddleware 
from sqlalchemy.orm import Session
from sqlalchemy import text

from app.core import get_db, log_event
from app.core.middleware.logging_middleware import LoggingMiddleware
from app.core.logging_config import setup_logging
from app.core.exceptions import (
    DatabaseConnectionError, db_connection_exception_handler,
    AuthenticationError, auth_exception_handler,
)
from app.core.security import BasicAuthMiddleware, require_api_auth
from app.core.rate_limit import RateLimiter, RateLimitMiddleware, cleanup_task
from app.api.v1.router import router as api_v1_router
from app.web.router import router as web_router

logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

rate_limiter = RateLimiter()

@asynccontextmanager
async def lifespan(app: FastAPI):
    setup_logging() 
    
    logger.info("Application startup: testing database connection...") # <-- This will now work
    db = None
    try:
        db = next(get_db())
        db.execute(text("SELECT 1"))
        logger.info("Database connection successful.") # <-- Update this too
        await log_event("api", "INFO", "Application started successfully.")
    except Exception as e:
        logger.critical(f"Database connection failed on startup: {e}") # <-- Update to logger.critical
        await log_event("api", "CRITICAL", f"Database connection failed on startup: {e}")
        raise DatabaseConnectionError("Could not connect to the database on startup.")
    finally:
        if db:
            db.close()

    # Start the rate limiter cleanup task
    cleanup_bg_task = asyncio.create_task(cleanup_task(rate_limiter))
    
    yield
    
    logger.info("Application shutdown.")
    await log_event("api", "INFO", "Application shutting down.")

    # Stop the cleanup task
    cleanup_bg_task.cancel()
    try:
        await cleanup_bg_task
    except asyncio.CancelledError:
        print("Rate limiter cleanup task cancelled.")

app = FastAPI(
    title="Unsubscribed Emails Tracker",
    version="1.0.0",
    lifespan=lifespan,
)

# --- Middleware ---
# NOTE: Order matters. Add CORS first.
app.add_middleware(LoggingMiddleware)
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],  # WARNING: Should be restricted in production
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)
app.add_middleware(RateLimitMiddleware, limiter=rate_limiter)
app.add_middleware(BasicAuthMiddleware)

# --- Exception Handlers ---
app.add_exception_handler(DatabaseConnectionError, db_connection_exception_handler)
app.add_exception_handler(AuthenticationError, auth_exception_handler)

# --- Routers ---
@app.get("/")
def root():
    """Root endpoint for basic service status."""
    return {"status": "ok", "service": "unsubscribed-emails-tracker"}

# Add the health check endpoint here to make it public
@app.get("/api/v1/health", tags=["Health"])
async def health_check(db: Session = Depends(get_db)):
    """Health check endpoint to verify service and database connectivity."""
    try:
        # Note: using text() is important for SQLAlchemy 2.0
        db.execute(text("SELECT 1"))
        return {"status": "healthy", "database": "connected"}
    except Exception as e:
        raise DatabaseConnectionError(f"Health check failed: {e}")
    
# API Router (all routes will be protected by require_api_auth)
app.include_router(
    api_v1_router,
    prefix="/api/v1",
    tags=["APIv1"],
    dependencies=[Depends(require_api_auth)]
)

# Web UI Router (routes are protected by BasicAuthMiddleware)
app.include_router(
    web_router,
    prefix="/web",
    tags=["Web"]
)