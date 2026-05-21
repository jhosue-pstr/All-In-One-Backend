import pytest
from app.main import app
from fastapi.testclient import TestClient

client = TestClient(app)

def test_read_root():
    response = client.get("/")
    assert response.status_code == 200

def test_health_check_ok():
    response = client.get("/health")
    assert response.status_code == 200
    assert response.json()["status"] == "healthy"

def test_health_check_fail(monkeypatch):
    from app.db.database import get_db
    class MockDB:
        def execute(self, *args, **kwargs):
            raise Exception("DB Error")
    
    app.dependency_overrides[get_db] = lambda: MockDB()
    response = client.get("/health")
    assert response.status_code == 200
    assert response.json()["status"] == "unhealthy"
    app.dependency_overrides.clear()