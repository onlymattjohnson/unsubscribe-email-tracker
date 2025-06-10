from fastapi.testclient import TestClient
from app.main import app
from app.core.exceptions import DatabaseConnectionError
from app.core.database import get_db

client = TestClient(app)

def test_root_endpoint():
    response = client.get("/")
    assert response.status_code == 200
    assert response.json() == {"status": "ok", "service": "unsubscribed-emails-tracker"}

def test_health_check_success(mocker):
    mock_db = mocker.MagicMock()
    app.dependency_overrides[get_db] = lambda: mock_db
    
    # Change the URL from "/health" to "/api/v1/health"
    response = client.get("/api/v1/health") 
    assert response.status_code == 200
    assert response.json() == {"status": "healthy", "database": "connected"}
    mock_db.execute.assert_called_once()
    
    app.dependency_overrides = {}

def test_health_check_db_failure(mocker):
    mock_db = mocker.MagicMock()
    mock_db.execute.side_effect = Exception("DB is down")
    app.dependency_overrides[get_db] = lambda: mock_db

    mocker.patch("app.core.exceptions.log_event")

    # Change the URL from "/health" to "/api/v1/health"
    response = client.get("/api/v1/health")
    assert response.status_code == 503
    assert response.json() == {"detail": "Service unavailable due to a database connection error."}
    
    app.dependency_overrides = {}
    
def test_cors_headers():
    response = client.get("/", headers={"Origin": "http://example.com"})
    assert response.headers["access-control-allow-origin"] == "*"