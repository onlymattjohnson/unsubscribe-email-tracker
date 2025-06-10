import pytest
from sqlalchemy import create_engine
from sqlalchemy.orm import sessionmaker
from sqlalchemy.exc import IntegrityError

from app.core.database import Base
from app.models import UnsubscribedEmail, Log

# Use an in-memory SQLite database for fast, isolated tests.
# This is great for model-level tests.
# For API tests, we will use a separate test Postgres DB.
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

def test_create_unsubscribed_email(db_session):
    """Test creating a valid UnsubscribedEmail instance."""
    email_data = {
        "sender_name": "Test Sender",
        "sender_email": "test@example.com",
        "unsub_method": "direct_link",
    }
    new_email = UnsubscribedEmail(**email_data)
    db_session.add(new_email)
    db_session.commit()
    db_session.refresh(new_email)

    assert new_email.id is not None
    assert new_email.sender_name == "Test Sender"
    assert new_email.unsub_method == "direct_link"
    assert new_email.inserted_at is not None

def test_unsubscribed_email_constraint(db_session):
    """Test the check constraint on unsub_method."""
    email_data = {
        "sender_name": "Invalid Sender",
        "sender_email": "invalid@example.com",
        "unsub_method": "invalid_method",  # This should fail
    }
    new_email = UnsubscribedEmail(**email_data)
    db_session.add(new_email)

    # We expect an IntegrityError because of the check constraint
    with pytest.raises(IntegrityError):
        db_session.commit()

def test_create_log(db_session):
    """Test creating a valid Log instance."""
    log_data = {
        "source_app": "test_suite",
        "log_level": "INFO",
        "message": "This is a test log message.",
        "details_json": {"user": "test", "action": "create"},
        "inserted_by": "pytest",
    }
    new_log = Log(**log_data)
    db_session.add(new_log)
    db_session.commit()
    db_session.refresh(new_log)

    assert new_log.id is not None
    assert new_log.source_app == "test_suite"
    assert new_log.details_json["user"] == "test"
    assert new_log.timestamp is not None