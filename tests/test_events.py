import os
import json
from fastapi.testclient import TestClient


def setup_test_db():
    os.environ["DATABASE_URL"] = "sqlite:///./test.db"


def test_ingest_and_dedupe(tmp_path):
    # ensure using test DB file
    os.environ["DATABASE_URL"] = f"sqlite:///{tmp_path / 'test.db'}"
    from app.main import app

    client = TestClient(app)

    payload = {
        "event_id": "e-123",
        "customer_id": "cust1",
        "resource_id": "res1",
        "resource_type": "vm",
        "usage": 2.5,
        "usage_unit": "vcpu-hour",
        "timestamp": "2026-06-20T00:00:00Z",
    }

    r = client.post("/events", json=payload)
    assert r.status_code == 201
    assert r.json()["status"] == "created"

    # duplicate
    r2 = client.post("/events", json=payload)
    assert r2.status_code == 200
    assert r2.json()["status"] == "duplicate"

    # query
    r3 = client.get("/events", params={"customer_id": "cust1"})
    assert r3.status_code == 200
    data = r3.json()
    assert data["events"] and data["events"][0]["event_id"] == "e-123"
