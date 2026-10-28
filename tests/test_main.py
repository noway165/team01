from fastapi.testclient import TestClient

from app import ai
from app.main import app

client = TestClient(app)


def test_root():
    response = client.get("/")
    assert response.status_code == 200
    assert "message" in response.json()


def test_health():
    response = client.get("/health")
    assert response.status_code == 200
    assert response.json() == {"status": "ok"}


def test_list_vehicles_empty():
    response = client.get("/vehicles")
    assert response.status_code == 200

def test_diagnose_parses_urgency(monkeypatch):
    monkeypatch.setattr(ai, "summarize_safe", lambda text: "HIGH\nWorn brake pads. Stop driving.")
    r = client.post("/diagnose", json={"symptom_text": "brakes squeal"})
    assert r.status_code == 200
    assert r.json()["urgency_level"] == "high"
    assert r.json()["ai_suggestion"] == "Worn brake pads. Stop driving."


def test_diagnose_unexpected_format_keeps_whole_answer(monkeypatch):
    monkeypatch.setattr(ai, "summarize_safe", lambda text: "Probably the battery.")
    r = client.post("/diagnose", json={"symptom_text": "car will not start"})
    assert r.json()["urgency_level"] == "unknown"
    assert r.json()["ai_suggestion"] == "Probably the battery."


def test_diagnose_ai_failure_gives_a_friendly_503(monkeypatch):
    def broken(text):
        raise ai.AIUnavailable("HTTP 403 (not retried)")

    monkeypatch.setattr(ai, "summarize_safe", broken)
    r = client.post("/diagnose", json={"symptom_text": "hello"})
    assert r.status_code == 503
    assert r.json()["message"].startswith("The AI feature is unavailable")
    assert "403" not in r.text  # the reason stays in the logs


def test_diagnose_empty_text_is_refused():
    assert client.post("/diagnose", json={"symptom_text": ""}).status_code == 422


def test_ui_page_loads():
    r = client.get("/ui")
    assert r.status_code == 200
    assert "/diagnose" in r.text
