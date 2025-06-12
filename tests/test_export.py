import pytest
import csv
import io
import json

from fastapi.testclient import TestClient

# Path fix might be needed
import sys, os
sys.path.insert(0, os.path.abspath(os.path.join(os.path.dirname(__file__), '..')))

from app.main import app
from app.core.config import settings
# Import the fixture from the other test file
from .test_unsubscribed_emails_filter import diverse_db

client = TestClient(app)
API_URL = "/api/v1/unsubscribed_emails/export"
AUTH_HEADERS = {"Authorization": f"Bearer {settings.API_TOKEN}"}

def test_export_csv_success(diverse_db):
    response = client.get(API_URL, headers=AUTH_HEADERS, params={"format": "csv"})
    assert response.status_code == 200
    assert response.headers["content-type"] == "text/csv; charset=utf-8"
    assert "attachment; filename=" in response.headers["content-disposition"]

    # Verify content
    content = response.text
    reader = csv.reader(io.StringIO(content))
    rows = list(reader)
    assert len(rows) == 4 # 1 header + 3 records
    assert rows[0] == ["sender_name", "sender_email", "unsub_method", "inserted_at"]
    assert rows[1][0] == "Tech Weekly"

def test_export_json_success(diverse_db):
    response = client.get(API_URL, headers=AUTH_HEADERS, params={"format": "json"})
    assert response.status_code == 200
    assert response.headers["content-type"] == "application/json"
    assert "attachment; filename=" in response.headers["content-disposition"]
    
    data = response.json()
    assert isinstance(data, list)
    assert len(data) == 3
    assert data[0]["sender_name"] == "Tech Weekly"

def test_export_with_filter(diverse_db):
    # Test CSV export with a filter
    response_csv = client.get(
        API_URL, 
        headers=AUTH_HEADERS, 
        params={"format": "csv", "unsub_method": "direct_link"}
    )
    assert response_csv.status_code == 200
    rows = list(csv.reader(io.StringIO(response_csv.text)))
    assert len(rows) == 3 # 1 header + 2 records