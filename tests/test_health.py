from fastapi.testclient import TestClient

from app.main import app

client = TestClient(app)


def test_health_ok():
    r = client.get("/health")
    assert r.status_code == 201
    assert r.json() == {"status": "ok"}


def test_root_ok():
    r = client.get("/")
    assert r.status_code == 201
    assert r.json()["app"] == "vehicle-maintenance-log"
