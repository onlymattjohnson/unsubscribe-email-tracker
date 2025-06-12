import pytest
from bs4 import BeautifulSoup
from fastapi.testclient import TestClient

# Import fixtures and helpers
from .test_unsubscribed_emails_filter import diverse_db
from .test_web_auth import get_basic_auth_headers
from app.core.config import settings

AUTH_HEADERS = get_basic_auth_headers(settings.BASIC_AUTH_USERNAME, settings.BASIC_AUTH_PASSWORD)
LIST_URL = "/web/unsubscribed"

def test_search_form_renders(test_client: TestClient, diverse_db):
    """Test that the search form and export buttons render."""
    response = test_client.get(LIST_URL, headers=AUTH_HEADERS)
    soup = BeautifulSoup(response.text, "html.parser")
    
    assert soup.find("form", class_="filter-form")
    assert soup.find("input", id="search")
    assert soup.find("a", string="Export as CSV")

def test_search_and_filter_results(test_client: TestClient, diverse_db):
    """Test submitting the search form and seeing filtered results."""
    params = {"search": "tech", "unsub_method": "direct_link"}
    response = test_client.get(LIST_URL, headers=AUTH_HEADERS, params=params)
    soup = BeautifulSoup(response.text, "html.parser")

    # Check that results are filtered
    assert "Showing 2 of 2 total" in soup.text
    assert len(soup.select("tbody tr")) == 2
    
    # Check that the form remembers the values
    assert soup.find("input", id="search")["value"] == "tech"
    assert soup.find("option", value="direct_link")["selected"] is not None

def test_filters_preserved_in_pagination(test_client: TestClient, populated_db_for_web): # from test_web_list
    """Test that filter query params are added to pagination links."""
    params = {"search": "Sender"}
    response = test_client.get(LIST_URL, headers=AUTH_HEADERS, params=params)
    soup = BeautifulSoup(response.text, "html.parser")
    
    next_link = soup.select_one('a[class="page-link"][href*="page=2"]')
    assert "search=Sender" in next_link["href"]