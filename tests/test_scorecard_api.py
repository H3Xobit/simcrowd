from fastapi.testclient import TestClient

from simcrowd.api.main import app


def test_scorecard_falls_back_to_sample():
    client = TestClient(app)
    res = client.get("/scorecard")
    assert res.status_code == 200
    data = res.json()
    assert "mean_mae" in data
    assert "questions" in data
    assert data.get("source") in {"sample", "artifacts"}


def test_scorecard_seed():
    client = TestClient(app)
    res = client.post("/scorecard/seed")
    assert res.status_code == 200
    assert res.json()["source"] == "sample"
    again = client.get("/scorecard")
    assert again.status_code == 200
    assert again.json().get("source") == "artifacts"
