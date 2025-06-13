import pytest
from fastapi.testclient import TestClient
from datetime import datetime, timedelta
from sqlalchemy.orm import Session

# Path fix might be needed
import sys, os

sys.path.insert(0, os.path.abspath(os.path.join(os.path.dirname(__file__), "..")))

from app.main import app
from app.core.config import settings
from app.core.database import SessionLocal
from app.models import UnsubscribedEmail

client = TestClient(app)
API_URL = "/api/v1/unsubscribed_emails/"
AUTH_HEADERS = {"Authorization": f"Bearer {settings.API_TOKEN}"}


@pytest.fixture(scope="function")
def diverse_db(db_session: Session):  # Change `db` to `db_session`
    """Fixture to create diverse data for filtering tests."""
    records = [
        UnsubscribedEmail(
            sender_name="Tech Weekly",
            sender_email="newsletter@tech.com",
            unsub_method="direct_link",
            inserted_at=datetime.now() - timedelta(days=10),
        ),
        UnsubscribedEmail(
            sender_name="Marketing Daily",
            sender_email="promo@marketing.com",
            unsub_method="isp_level",
            inserted_at=datetime.now() - timedelta(days=5),
        ),
        UnsubscribedEmail(
            sender_name="Cool Gadgets",
            sender_email="gadgets@tech.com",
            unsub_method="direct_link",
            inserted_at=datetime.now() - timedelta(days=1),
        ),
    ]
    db_session.add_all(records)
    db_session.commit()
    yield records


def test_filter_by_unsub_method(test_client: TestClient, diverse_db):
    response = test_client.get(
        API_URL, headers=AUTH_HEADERS, params={"unsub_method": "isp_level"}
    )
    assert response.status_code == 200
    data = response.json()
    assert data["total"] == 1
    assert data["items"][0]["sender_name"] == "Marketing Daily"


def test_search(test_client: TestClient, diverse_db):
    # Search by part of the name, case-insensitive
    response = test_client.get(
        API_URL, headers=AUTH_HEADERS, params={"search": "daily"}
    )
    assert response.status_code == 200
    assert response.json()["total"] == 1
    assert response.json()["items"][0]["sender_name"] == "Marketing Daily"

    # Search by part of the email domain
    response = client.get(API_URL, headers=AUTH_HEADERS, params={"search": "tech.com"})
    assert response.status_code == 200
    assert response.json()["total"] == 2


def test_filter_by_date_from(test_client: TestClient, diverse_db):
    date_str = (datetime.now() - timedelta(days=6)).isoformat()
    response = test_client.get(
        API_URL, headers=AUTH_HEADERS, params={"date_from": date_str}
    )
    assert response.status_code == 200
    assert response.json()["total"] == 2  # Marketing Daily and Cool Gadgets


def test_combine_filters(test_client: TestClient, diverse_db):
    # Search for 'tech' but only with 'direct_link' method
    response = test_client.get(
        API_URL,
        headers=AUTH_HEADERS,
        params={"search": "tech", "unsub_method": "direct_link"},
    )
    assert response.status_code == 200
    data = response.json()
    assert data["total"] == 2
    # Ensure all returned items match the method
    assert all(item["unsub_method"] == "direct_link" for item in data["items"])
