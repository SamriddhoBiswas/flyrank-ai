import pytest
import asyncio
from fastapi.testclient import TestClient
from main import app, ip_request_timestamps
from repository import repo

client = TestClient(app)

@pytest.fixture(autouse=True)
def reset_state():
    ip_request_timestamps.clear()
    repo.provider_a_enabled = True
    repo.provider_b_enabled = True
    repo.email_side_effect_enabled = True

def test_probe_1_valid_submission():
    """PROBE 1 — POST valid submission -> stored, 2xx, visible via dashboard API."""
    payload = {
        "widget_id": "demo-widget-id",
        "name": "Jane Doe",
        "email": "jane@example.com",
        "message": "Valid test submission"
    }
    resp = client.post("/api/v1/submissions", json=payload)
    assert resp.status_code == 201
    data = resp.json()
    assert data["status"] == "success"
    assert "submission_id" in data

    # Verify visible via dashboard API
    dash_resp = client.get("/api/v1/dashboard/submissions")
    assert dash_resp.status_code == 200
    subs = dash_resp.json()["submissions"]
    assert any(s["email"] == "jane@example.com" for s in subs)

def test_probe_2_malformed_and_oversized_payload():
    """PROBE 2 — Send malformed payload (400) and oversized payload (413)."""
    # Malformed Payload (missing required email)
    bad_payload = {"widget_id": "demo-widget-id", "name": "J"}
    resp_bad = client.post("/api/v1/submissions", json=bad_payload)
    assert resp_bad.status_code == 400

    # Oversized Payload (> 100 KB)
    huge_message = "A" * 150000
    huge_payload = {
        "widget_id": "demo-widget-id",
        "name": "Big Sender",
        "email": "big@example.com",
        "message": huge_message
    }
    resp_huge = client.post("/api/v1/submissions", json=huge_payload)
    assert resp_huge.status_code == 413

def test_probe_3_rate_limiting_burst():
    """PROBE 3 — Fire a burst of rapid submissions -> 429s appear."""
    payload = {
        "widget_id": "demo-widget-id",
        "name": "Burst Tester",
        "email": "burst@example.com",
        "message": "Testing rate limit burst"
    }
    responses = [client.post("/api/v1/submissions", json=payload) for _ in range(7)]
    status_codes = [r.status_code for r in responses]
    assert 429 in status_codes

def test_probe_4_geo_fallback_chain():
    """PROBE 4 — Disable Provider A -> Provider B enriches. Disable both -> stored without geo."""
    payload = {
        "widget_id": "demo-widget-id",
        "name": "Geo Tester",
        "email": "geo@example.com",
        "message": "Testing geo fallback chain"
    }

    # Disable Provider A
    repo.provider_a_enabled = False
    resp1 = client.post("/api/v1/submissions", json=payload)
    assert resp1.status_code == 201
    assert "Provider B" in resp1.json()["geo_enriched"]["provider_used"] or "None" in resp1.json()["geo_enriched"]["provider_used"]

    # Disable both providers
    repo.provider_b_enabled = False
    resp2 = client.post("/api/v1/submissions", json=payload)
    assert resp2.status_code == 201
    assert resp2.json()["geo_enriched"]["provider_used"] == "None (Degraded)"

def test_probe_5_email_side_effect_failure_tolerance():
    """PROBE 5 — Force email side effect to throw -> submission still succeeds and is stored."""
    repo.email_side_effect_enabled = False
    payload = {
        "widget_id": "demo-widget-id",
        "name": "Side Effect Tester",
        "email": "sideeffect@example.com",
        "message": "Testing safe side effect failure tolerance"
    }
    resp = client.post("/api/v1/submissions", json=payload)
    assert resp.status_code == 201
    assert resp.json()["status"] == "success"

def test_probe_6_honeypot_spam_filter():
    """PROBE 6 — Fill honeypot field like a bot -> submission silently dropped."""
    bot_payload = {
        "widget_id": "demo-widget-id",
        "name": "Bot User",
        "email": "bot@spam.com",
        "message": "Buy cheap stuff",
        "bot_field": "I am a spam bot"
    }
    resp = client.post("/api/v1/submissions", json=bot_payload)
    assert resp.status_code == 200
    assert resp.json()["message"] == "Submission received."
