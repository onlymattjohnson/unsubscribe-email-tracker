from fastapi.testclient import TestClient
from app.main import app
from app.core.exceptions import DatabaseConnectionError

client = TestClient(app)

def test_root_endpoint():
    response = client.get("/")
    assert response.status_code == 200
    assert response.json() == {"status": "ok", "service": "unsubscribed-emails-tracker"}

def test_health_check_success(mocker):
    # Mock get_db to avoid real DB dependency in this unit test
    mock_db = mocker.MagicMock()
    app.dependency_overrides[app.get("/health").dependencies[0].dependency] = lambda: mock_db
    
    response = client.get("/health")
    assert response.status_code == 200
    assert response.json() == {"status": "healthy", "database": "connected"}
    mock_db.execute.assert_called_once()
    
    # Clean up the override
    app.dependency_overrides = {}

def test_health_check_db_failure(mocker):
    mock_db = mocker.MagicMock()
    mock_db.execute.side_effect = Exception("DB is down")
    app.dependency_overrides[app.get("/health").dependencies[0].dependency] = lambda: mock_db

    # Mock the logging function to prevent file I/O during test
    mocker.patch("app.core.exceptions.log_event")

    response = client.get("/health")
    assert response.status_code == 503
    assert response.json() == {"detail": "Service unavailable due to a database connection error."}
    
    # Clean up the override
    app.dependency_overrides = {}

def test_cors_headers():
    response = client.get("/", headers={"Origin": "http://example.com"})
    assert response.headers["access-control-allow-origin"] == "*"