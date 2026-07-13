from pathlib import Path

from simcrowd.panel.persona_writer import write_persona
from simcrowd.panel.sampler import load_records, to_attributes, weighted_sample
from simcrowd.research.compiler import load_spec
from simcrowd.research.runner import load_personas, run_study
from simcrowd.synthesis.report import build_report


def _write_panel(tmp_path: Path, n: int = 20, seed: int = 7) -> Path:
    records = load_records(Path("data/census/sample.jsonl"))
    drawn = weighted_sample(records, n, seed=seed)
    panel_path = tmp_path / "personas.jsonl"
    with panel_path.open("w", encoding="utf-8") as f:
        for i, rec in enumerate(drawn, start=1):
            p = write_persona(
                panel_id="panel_test",
                idx=i,
                attributes=to_attributes(rec),
                weight=float(rec["weight"]),
            )
            f.write(p.model_dump_json() + "\n")
    return panel_path


def test_survey_consistency_and_reproducibility(tmp_path: Path):
    panel_path = _write_panel(tmp_path)
    # ensure real newlines
    text = panel_path.read_text(encoding="utf-8")
    if "\\n" in text:
        panel_path.write_text(text.replace("\\n", "\n"), encoding="utf-8")
    spec = load_spec(Path("data/concepts/fintech_survey.json"))
    personas = load_personas(panel_path)
    a = run_study(spec, personas, seed=42)
    b = run_study(spec, personas, seed=42)
    assert a["responses"] == b["responses"]
    assert a["consistency_rate"] >= 0.9
    report = build_report(spec, a, personas)
    assert report.verification_ok


def test_interview_study(tmp_path: Path):
    panel_path = _write_panel(tmp_path, n=5)
    text = panel_path.read_text(encoding="utf-8")
    if "\\n" in text:
        panel_path.write_text(text.replace("\\n", "\n"), encoding="utf-8")
    spec = load_spec(Path("data/concepts/fintech_interview.json"))
    personas = load_personas(panel_path)
    result = run_study(spec, personas, seed=1)
    assert result["n"] == 5
    assert all(r["answers"] for r in result["responses"])
