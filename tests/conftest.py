import pytest
from fastapi.testclient import TestClient
from sqlalchemy import create_engine
from sqlalchemy.orm import sessionmaker, Session

from app.core.config import settings
from app.main import app
from app.core.database import Base, get_db

# Use the test database URL from our settings
SQLALCHEMY_DATABASE_URL = settings.TEST_DATABASE_URL
if not SQLALCHEMY_DATABASE_URL:
    raise ValueError("TEST_DATABASE_URL environment variable is not set for testing.")

# Create a new SQLAlchemy engine for testing
engine = create_engine(SQLALCHEMY_DATABASE_URL)

# Create a new SessionLocal class for testing that uses the test engine
TestingSessionLocal = sessionmaker(autocommit=False, autoflush=False, bind=engine)


@pytest.fixture(scope="function")
def db_session() -> Session:
    """
    This is the core fixture that provides a clean database state for each test.
    - It drops and recreates all tables for every single test function.
    - It yields a single session for the test to use.
    """
    # Before the test runs, drop all tables and recreate them
    Base.metadata.drop_all(bind=engine)
    Base.metadata.create_all(bind=engine)

    db = TestingSessionLocal()
    try:
        yield db
    finally:
        db.close()


@pytest.fixture(scope="function")
def test_client(db_session: Session) -> TestClient:
    """
    This fixture provides a TestClient that is configured to use the
    isolated database session from the `db_session` fixture.
    """
    def override_get_db():
        """This function will replace the original `get_db` dependency."""
        try:
            yield db_session
        finally:
            db_session.close()

    # Apply the override
    app.dependency_overrides[get_db] = override_get_db
    
    # Yield the configured client
    yield TestClient(app)
    
    # Remove the override after the test is done
    app.dependency_overrides.clear()