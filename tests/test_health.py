from fastapi.testclient import TestClient
import os


def test_health():
    # ensure DB path is test-specific
    os.environ.setdefault("DATABASE_URL", "sqlite:///./test.db")
    from app.main import app

    client = TestClient(app)
    r = client.get("/health")
    assert r.status_code == 200
    assert r.json() == {"status": "ok"}
