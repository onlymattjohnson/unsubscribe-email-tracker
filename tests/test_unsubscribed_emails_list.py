import pytest
import time
from fastapi.testclient import TestClient

# Path fix might be needed
import sys, os
sys.path.insert(0, os.path.abspath(os.path.join(os.path.dirname(__file__), '..')))

from app.main import app
from app.core.config import settings
from app.core.database import SessionLocal
from app.models import UnsubscribedEmail

client = TestClient(app)
API_URL = "/api/v1/unsubscribed_emails/"
AUTH_HEADERS = {"Authorization": f"Bearer {settings.API_TOKEN}"}

@pytest.fixture(scope="module")
def db_session():
    """Fixture to provide a database session for test setup."""
    db = SessionLocal()
    yield db
    db.close()

@pytest.fixture(scope="function")
def populate_db(db_session):
    """Fixture to create 25 test records and clean them up afterward."""
    # Start by clearing any existing data to ensure a clean slate
    db_session.query(UnsubscribedEmail).delete()
    db_session.commit()

    created_emails = []
    for i in range(25):
        email = UnsubscribedEmail(
            sender_name=f"Test Sender {i}",
            sender_email=f"sender{i}@example.com",
            unsub_method="direct_link"
        )
        created_emails.append(email)
        db_session.add(email)
        db_session.commit() # Commit each one to get a unique timestamp
        time.sleep(0.001) # Add a tiny delay
    
    # The API will sort by desc, so the highest ID (24) will be first
    yield created_emails
    
    # Cleanup
    db_session.query(UnsubscribedEmail).delete()
    db_session.commit()
    
def test_list_empty(db_session):
    # Ensure DB is empty for this test
    db_session.query(UnsubscribedEmail).delete()
    db_session.commit()
    response = client.get(API_URL, headers=AUTH_HEADERS)
    assert response.status_code == 200
    data = response.json()
    assert data["items"] == []
    assert data["total"] == 0
    assert data["limit"] == 10
    assert data["offset"] == 0

def test_list_with_default_pagination(populate_db):
    response = client.get(API_URL, headers=AUTH_HEADERS)
    assert response.status_code == 200
    data = response.json()
    
    assert data["total"] == 25
    assert data["limit"] == 10
    assert data["offset"] == 0
    assert len(data["items"]) == 10
    # Check that the first item returned is the last one created (newest first)
    assert data["items"][0]["sender_name"] == "Test Sender 24"

def test_list_with_custom_pagination(populate_db):
    response = client.get(API_URL, headers=AUTH_HEADERS, params={"limit": 5, "offset": 5})
    assert response.status_code == 200
    data = response.json()
    
    assert data["total"] == 25
    assert data["limit"] == 5
    assert data["offset"] == 5
    assert len(data["items"]) == 5
    # The 6th item (offset 5) should be Sender 19 (24, 23, 22, 21, 20 are skipped)
    assert data["items"][0]["sender_name"] == "Test Sender 19"

def test_list_limit_validation():
    # Test over max limit
    response = client.get(API_URL, headers=AUTH_HEADERS, params={"limit": 200})
    assert response.status_code == 422
    
    # Test under min limit
    response = client.get(API_URL, headers=AUTH_HEADERS, params={"limit": 0})
    assert response.status_code == 422