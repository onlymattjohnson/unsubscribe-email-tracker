from fastapi import FastAPI, Depends, status
from fastapi.testclient import TestClient
from app.api.deps import verify_token
from app.core.config import settings

# Create a minimal app for testing the dependency
test_app = FastAPI()

@test_app.get("/secure-resource")
async def secure_resource(token: str = Depends(verify_token)):
    return {"status": "ok", "token": token}

client = TestClient(test_app)

def test_verify_token_success():
    headers = {"Authorization": f"Bearer {settings.API_TOKEN}"}
    response = client.get("/secure-resource", headers=headers)
    assert response.status_code == 200
    assert response.json() == {"status": "ok", "token": settings.API_TOKEN}

def test_verify_token_missing_header():
    response = client.get("/secure-resource")
    assert response.status_code == status.HTTP_401_UNAUTHORIZED
    assert "Not authenticated" in response.json()["detail"]

def test_verify_token_invalid_scheme():
    headers = {"Authorization": f"Basic {settings.API_TOKEN}"}
    response = client.get("/secure-resource", headers=headers)
    assert response.status_code == status.HTTP_401_UNAUTHORIZED
    assert "Not authenticated" in response.json()["detail"]

def test_verify_token_incorrect_token():
    headers = {"Authorization": "Bearer wrongtoken"}
    response = client.get("/secure-resource", headers=headers)
    assert response.status_code == status.HTTP_401_UNAUTHORIZED
    assert response.json()["detail"] == "Invalid or expired token"