import pytest
from sqlalchemy import create_engine
from sqlalchemy.orm import sessionmaker

# Path fix may be needed if you removed it from other files
import sys, os
sys.path.insert(0, os.path.abspath(os.path.join(os.path.dirname(__file__), '..')))

from app.core.database import Base

# Use an in-memory SQLite database for fast, isolated tests.
SQLALCHEMY_DATABASE_URL = "sqlite:///:memory:"

engine = create_engine(
    SQLALCHEMY_DATABASE_URL, connect_args={"check_same_thread": False}
)
TestingSessionLocal = sessionmaker(autocommit=False, autoflush=False, bind=engine)


@pytest.fixture(scope="function")
def db_session():
    """
    Pytest fixture to create a new database session for each test function.
    It creates all tables, yields a session, and then drops all tables.
    """
    Base.metadata.create_all(bind=engine)
    session = TestingSessionLocal()
    try:
        yield session
    finally:
        session.close()
        Base.metadata.drop_all(bind=engine)