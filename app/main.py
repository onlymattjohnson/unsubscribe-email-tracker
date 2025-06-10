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
from app.api.v1.router import router as api_v1_router
from app.web.router import router as web_router

@asynccontextmanager
async def lifespan(app: FastAPI):
    setup_logging() 
    logger.info("Starting up...")
    
    print("Application startup: testing database connection...")
    db = None
    try:
        db = next(get_db())
        db.execute(text("SELECT 1"))
        print("Database connection successful.")
        await log_event("api", "INFO", "Application started successfully.")
    except Exception as e:
        print(f"FATAL: Database connection failed on startup: {e}")
        await log_event("api", "CRITICAL", f"Database connection failed on startup: {e}")
        raise DatabaseConnectionError("Could not connect to the database on startup.")
    finally:
        if db:
            db.close()
    
    yield
    
    logger.info("Shutting down...")
    print("Application shutdown.")
    await log_event("api", "INFO", "Application shutting down.")


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
    dependencies=[require_api_auth]
)

# Web UI Router (routes are protected by BasicAuthMiddleware)
app.include_router(
    web_router,
    prefix="/web",
    tags=["Web"]
)