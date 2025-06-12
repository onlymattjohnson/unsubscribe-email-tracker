import pytest
import csv
import io
import json

from app.models import UnsubscribedEmail
from app.core.config import settings
from sqlalchemy.orm import Session
from fastapi.testclient import TestClient

from .test_unsubscribed_emails_filter import diverse_db

API_URL = "/api/v1/unsubscribed_emails/export"
AUTH_HEADERS = {"Authorization": f"Bearer {settings.API_TOKEN}"}

def test_export_csv_success(test_client: TestClient, diverse_db):
    response = test_client.get(API_URL, headers=AUTH_HEADERS, params={"format": "csv"})
    assert response.status_code == 200
    assert response.headers["content-type"].startswith("text/csv")
    assert "attachment; filename=" in response.headers["content-disposition"]

    # Verify content
    content = response.text
    reader = csv.reader(io.StringIO(content))
    rows = list(reader)
    
    assert len(rows) == 4 # 1 header + 3 records
    assert rows[0] == ["id", "sender_name", "sender_email", "unsub_method", "inserted_at"]
    assert rows[1][1] == "Cool Gadgets"
    assert rows[1][0] == '3'

def test_export_json_success(test_client: TestClient, diverse_db):
    response = test_client.get(API_URL, headers=AUTH_HEADERS, params={"format": "json"})
    assert response.status_code == 200
    assert response.headers["content-type"] == "application/json"
    
    data = response.json()
    assert isinstance(data, list)
    assert len(data) == 3
    assert data[0]["sender_name"] == "Cool Gadgets"

def test_export_with_filter(test_client: TestClient, diverse_db):
    response_csv = test_client.get( # Use test_client here
        API_URL, 
        headers=AUTH_HEADERS, 
        params={"format": "csv", "unsub_method": "direct_link"}
    )
    assert response_csv.status_code == 200
    rows = list(csv.reader(io.StringIO(response_csv.text)))
    assert len(rows) == 3 # 1 header + 2 records