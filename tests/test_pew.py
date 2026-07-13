from pathlib import Path

from simcrowd.panel.persona_writer import write_persona
from simcrowd.panel.sampler import load_records, to_attributes, weighted_sample
from simcrowd.validation.pew_bench import load_topline, run_panel_pew, scorecard


def test_pew_scorecard_smoke(tmp_path: Path):
    records = load_records(Path("data/census/sample.jsonl"))
    drawn = weighted_sample(records, 20, seed=3)
    panel_path = tmp_path / "personas.jsonl"
    with panel_path.open("w", encoding="utf-8") as f:
        for i, rec in enumerate(drawn, start=1):
            p = write_persona(
                panel_id="panel_pew",
                idx=i,
                attributes=to_attributes(rec),
                weight=float(rec["weight"]),
            )
            f.write(p.model_dump_json() + "\n")
    truth = {}
    truth.update(load_topline(Path("data/pew/tech_adoption_topline.csv")))
    truth.update(load_topline(Path("data/pew/consumer_attitudes_topline.csv")))
    synth = run_panel_pew(panel_path, seed=42)
    card = scorecard(synth, truth)
    assert "mean_mae" in card
    assert "directional_agreement_rate" in card
    assert len(card["questions"]) >= 4
