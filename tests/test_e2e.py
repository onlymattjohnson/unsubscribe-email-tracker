import pytest
import csv
import io
import json
from fastapi.testclient import TestClient
from sqlalchemy.orm import Session

from app.core.config import settings
from app.models import UnsubscribedEmail

# Define headers once
AUTH_HEADERS = {"Authorization": f"Bearer {settings.API_TOKEN}"}

@pytest.fixture(scope="function")
def e2e_data(db_session: Session):
    """A specific data set for the E2E test."""
    records = [
        UnsubscribedEmail(sender_name="E2E Company A", sender_email="contact@e2e-a.com", unsub_method="direct_link"),
        UnsubscribedEmail(sender_name="E2E Company B", sender_email="support@e2e-b.com", unsub_method="isp_level"),
    ]
    db_session.add_all(records)
    db_session.commit()
    # Return the objects so we can access their properties
    for r in records:
        db_session.refresh(r)
    yield records

def test_full_workflow(test_client: TestClient, e2e_data):
    """
    Tests the complete user workflow: create, list, filter, and export.
    """
    # === 1. LIST: Verify initial data is present ===
    list_response = test_client.get("/api/v1/unsubscribed_emails/", headers=AUTH_HEADERS)
    assert list_response.status_code == 200
    list_data = list_response.json()
    assert list_data["total"] >= 2 # Should be at least our 2 records
    assert list_data["items"][0]["sender_name"] == "E2E Company B" # Newest first

    # === 2. FILTER: Search for a specific record ===
    filter_params = {"search": "e2e-a.com"}
    filter_response = test_client.get("/api/v1/unsubscribed_emails/", headers=AUTH_HEADERS, params=filter_params)
    assert filter_response.status_code == 200
    filter_data = filter_response.json()
    assert filter_data["total"] == 1
    assert filter_data["items"][0]["sender_name"] == "E2E Company A"
    
    # Store the ID for later checks
    record_id = filter_data["items"][0]["id"]
    
    # === 3. EXPORT (CSV): Export the filtered data ===
    export_params_csv = {"search": "e2e-a.com", "format": "csv"}
    export_response_csv = test_client.get("/api/v1/unsubscribed_emails/export", headers=AUTH_HEADERS, params=export_params_csv)
    assert export_response_csv.status_code == 200
    assert export_response_csv.headers["content-type"].startswith("text/csv")
    
    # Verify CSV content
    reader = csv.reader(io.StringIO(export_response_csv.text))
    rows = list(reader)
    assert len(rows) == 2 # Header + 1 data row
    assert rows[0][0] == "id" # Check headers
    assert rows[1][0] == str(record_id) # Check ID
    assert rows[1][1] == "E2E Company A" # Check name

    # === 4. EXPORT (JSON): Export the filtered data ===
    export_params_json = {"search": "e2e-a.com", "format": "json"}
    export_response_json = test_client.get("/api/v1/unsubscribed_emails/export", headers=AUTH_HEADERS, params=export_params_json)
    assert export_response_json.status_code == 200
    assert export_response_json.headers["content-type"] == "application/json"
    
    # Verify JSON content
    json_data = export_response_json.json()
    assert len(json_data) == 1
    assert json_data[0]["id"] == record_id
    assert json_data[0]["sender_name"] == "E2E Company A"