from fastapi.testclient import TestClient

from app.main import app

client = TestClient(app)


def test_health_ok():
    r = client.get("/health")
    assert r.status_code == 200
    assert r.json() == {"status": "ok"}


def test_root_ok():
    r = client.get("/")
    assert r.status_code == 200
    assert r.json()["app"] == "vehicle-maintenance-log"


def test_health_db_without_database():
    # The pool is never opened in tests: the route must answer 503, not crash.
    r = client.get("/health/db")
    assert r.status_code == 503
    assert r.json() == {"db": "error"}
