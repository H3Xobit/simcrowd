import json
from pathlib import Path

from fastapi.testclient import TestClient

from simcrowd.api.main import app
from simcrowd.validation.pew_bench import scorecard_to_csv


def test_scorecard_to_csv_headers():
    card = json.loads(Path("data/pew/sample_scorecard.json").read_text(encoding="utf-8"))
    text = scorecard_to_csv(card)
    assert text.splitlines()[0].startswith("question_id,mae,js,")
    assert "tech_ai_interest" in text


def test_scorecard_csv_endpoint():
    client = TestClient(app)
    res = client.get("/scorecard.csv")
    assert res.status_code == 200
    assert "question_id" in res.text
    assert "mae" in res.text
