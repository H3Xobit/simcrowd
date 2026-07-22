from fastapi.testclient import TestClient

from simcrowd.api.main import app


def test_list_concepts():
    client = TestClient(app)
    res = client.get("/concepts")
    assert res.status_code == 200
    rows = res.json()
    assert isinstance(rows, list)
    assert len(rows) >= 3
    assert any("fintech" in r["id"] or "fintech" in r["path"] for r in rows)
