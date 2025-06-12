import pytest
from bs4 import BeautifulSoup
from fastapi.testclient import TestClient
from sqlalchemy.orm import Session

from app.core.config import settings
from app.models import UnsubscribedEmail

# Helper from previous step
from .test_web_auth import get_basic_auth_headers

AUTH_HEADERS = get_basic_auth_headers(settings.BASIC_AUTH_USERNAME, settings.BASIC_AUTH_PASSWORD)
LIST_URL = "/web/unsubscribed"

def test_list_view_empty_state(test_client: TestClient):
    """Test that the empty state message is shown."""
    response = test_client.get(LIST_URL, headers=AUTH_HEADERS)
    assert response.status_code == 200
    soup = BeautifulSoup(response.text, "html.parser")
    assert "No Records Found" in soup.text
    assert soup.find("table") is None


def test_list_view_first_page(
    test_client: TestClient, 
    populated_db_for_web,
    db_session: Session # <-- Add the db_session fixture here
):
    """Test the first page of a populated list."""

    # --- DEBUGGING STEP ---
    count = db_session.query(UnsubscribedEmail).count()
    print(f"\n--- Database count before request: {count} ---\n")
    # --- END DEBUGGING ---

    response = test_client.get(LIST_URL, headers=AUTH_HEADERS)
    assert response.status_code == 200
    soup = BeautifulSoup(response.text, "html.parser")
    
    table_rows = soup.select("tbody tr")
    assert len(table_rows) == 20 # ITEMS_PER_PAGE
    assert "Sender 49" in table_rows[0].text # Newest first

    # Check pagination controls
    assert "Page 1 of 3" in soup.text
    prev_link = soup.select_one('a[href="?page=0"]')
    assert not prev_link or "disabled" in prev_link.parent.get("class", [])

def test_list_view_second_page(test_client: TestClient, populated_db_for_web):
    """Test navigating to the second page."""
    response = test_client.get(f"{LIST_URL}?page=2", headers=AUTH_HEADERS)
    assert response.status_code == 200
    soup = BeautifulSoup(response.text, "html.parser")

    table_rows = soup.select("tbody tr")
    assert len(table_rows) == 20
    # Newest-first: Page 1 (IDs 49-30), Page 2 (IDs 29-10)
    assert "Sender 29" in table_rows[0].text
    assert "Page 2 of 3" in soup.text