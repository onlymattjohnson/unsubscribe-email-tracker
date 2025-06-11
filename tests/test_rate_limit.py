import time
import asyncio
import pytest
from fastapi.testclient import TestClient

# Path fix might be needed
import sys, os
sys.path.insert(0, os.path.abspath(os.path.join(os.path.dirname(__file__), '..')))

from app.main import app, rate_limiter
from app.core.config import settings

client = TestClient(app)

@pytest.fixture(autouse=True)
def cleanup_rate_limiter():
    """Fixture to clean the rate limiter state before each test."""
    rate_limiter._requests.clear()
    yield

def test_rate_limit_under_limit():
    headers = {"Authorization": f"Bearer {settings.API_TOKEN}"}
    for _ in range(5):
        response = client.get("/api/v1/health", headers=headers)
        assert response.status_code == 200

def test_rate_limit_exceeded_ip():
    # Anonymous requests are identified by IP. TestClient uses 'testclient'.
    limit = settings.RATE_LIMIT_REQUESTS
    
    for _ in range(limit):
        response = client.get("/") # Use a public endpoint
        assert response.status_code == 200
        
    # The next request should be blocked
    response = client.get("/")
    assert response.status_code == 429
    assert "Retry-After" in response.headers
    assert int(response.headers["Retry-After"]) > 0

def test_sliding_window(mocker):
    # Mock time to control the window precisely
    start_time = time.time()
    mock_time = mocker.patch("time.time")
    mock_time.return_value = start_time

    limit = settings.RATE_LIMIT_REQUESTS
    window = settings.RATE_LIMIT_TIMESCALE_SECONDS

    # Make 'limit - 1' requests
    for _ in range(limit - 1):
        client.get("/")

    # Move time forward by half the window
    mock_time.return_value = start_time + (window / 2)
    
    # This request should be fine
    response = client.get("/")
    assert response.status_code == 200
    
    # This request should be blocked
    response = client.get("/")
    assert response.status_code == 429
    
    # Move time forward so the first batch of requests expires
    mock_time.return_value = start_time + window + 1
    
    # This request should now be fine again
    response = client.get("/")
    assert response.status_code == 200

def test_cleanup_function(mocker):
    # Setup limiter with old and new data
    now = time.time()
    old_time = now - settings.RATE_LIMIT_TIMESCALE_SECONDS - 100
    rate_limiter._requests = {
        "user1": [old_time, old_time], # Should be removed
        "user2": [now - 10, now - 5],   # Should be kept
        "user3": [old_time]             # Should be removed entirely
    }
    
    # Run cleanup
    asyncio.run(rate_limiter.cleanup())
    
    assert "user1" not in rate_limiter._requests
    assert "user3" not in rate_limiter._requests
    assert "user2" in rate_limiter._requests
    assert len(rate_limiter._requests["user2"]) == 2