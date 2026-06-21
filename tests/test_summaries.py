import os
from fastapi.testclient import TestClient


def test_summaries(tmp_path):
    os.environ["DATABASE_URL"] = f"sqlite:///{tmp_path / 'test.db'}"
    from app.main import app

    client = TestClient(app)

    events = [
        {
            "event_id": "s1",
            "customer_id": "custA",
            "resource_id": "r1",
            "resource_type": "vm",
            "usage": 1.0,
            "usage_unit": "vcpu-hour",
            "timestamp": "2026-06-20T01:00:00Z",
        },
        {
            "event_id": "s2",
            "customer_id": "custA",
            "resource_id": "r2",
            "resource_type": "vm",
            "usage": 3.0,
            "usage_unit": "vcpu-hour",
            "timestamp": "2026-06-20T05:00:00Z",
        },
    ]

    for e in events:
        r = client.post("/events", json=e)
        assert r.status_code in (200, 201)

    r = client.get("/summaries", params={"customer_id": "custA", "granularity": "day"})
    assert r.status_code == 200
    body = r.json()
    assert body["customer_id"] == "custA"
    assert body["buckets"]
    assert body["buckets"][0]["usage_total"] == 4.0
