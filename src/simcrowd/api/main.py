"""FastAPI surface for SimCrowd."""

from __future__ import annotations

import json
from pathlib import Path
from typing import Any

from fastapi import FastAPI, HTTPException
from fastapi.middleware.cors import CORSMiddleware

from simcrowd import __version__
from simcrowd.models import HealthResponse
from simcrowd.panel.persona_writer import write_persona
from simcrowd.panel.sampler import load_records, to_attributes, weighted_sample
from simcrowd.research.compiler import load_spec
from simcrowd.research.runner import load_personas, run_study
from simcrowd.settings import get_settings
from simcrowd.synthesis.report import build_report

app = FastAPI(title="SimCrowd API", version=__version__)
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_methods=["*"],
    allow_headers=["*"],
)

ARTIFACTS = Path("artifacts")
ARTIFACTS.mkdir(exist_ok=True)


@app.get("/health", response_model=HealthResponse)
def health() -> HealthResponse:
    return HealthResponse(status="ok", version=__version__)


@app.post("/panels")
def create_panel(size: int = 40, seed: int | None = None) -> dict[str, Any]:
    settings = get_settings()
    seed = settings.sc_seed if seed is None else seed
    panel_id = f"panel_{seed}_{size}"
    records = load_records(Path("data/census/sample.jsonl"))
    drawn = weighted_sample(records, size, seed)
    personas = [
        write_persona(
            panel_id=panel_id,
            idx=i,
            attributes=to_attributes(rec),
            weight=float(rec["weight"]),
        )
        for i, rec in enumerate(drawn, start=1)
    ]
    out = ARTIFACTS / f"{panel_id}.jsonl"
    with out.open("w", encoding="utf-8") as f:
        for p in personas:
            f.write(p.model_dump_json() + "\n")
    return {"panel_id": panel_id, "size": size, "seed": seed, "path": str(out)}


@app.get("/panels")
def list_panels() -> list[dict[str, str]]:
    return [{"path": str(p.name)} for p in sorted(ARTIFACTS.glob("panel_*.jsonl"))]


@app.post("/studies")
def create_study(
    spec_path: str = "data/concepts/fintech_survey.json",
    panel_path: str | None = None,
    seed: int | None = None,
) -> dict[str, Any]:
    settings = get_settings()
    seed = settings.sc_seed if seed is None else seed
    if panel_path is None:
        panels = sorted(ARTIFACTS.glob("panel_*.jsonl"))
        if not panels:
            raise HTTPException(400, "no panel found; POST /panels first")
        panel_path = str(panels[-1])
    spec = load_spec(Path(spec_path))
    personas = load_personas(Path(panel_path))
    result = run_study(spec, personas, seed)
    report = build_report(spec, result, personas)
    result["report"] = report.model_dump()
    out = ARTIFACTS / f"study_{spec.id}.json"
    out.write_text(json.dumps(result, indent=2), encoding="utf-8")
    return {
        "study_id": spec.id,
        "n": result["n"],
        "attention_pass_rate": result["attention_pass_rate"],
        "consistency_rate": result["consistency_rate"],
        "cost_usd": result["cost_usd"],
        "report_id": report.id,
        "verification_ok": report.verification_ok,
        "path": str(out),
    }


@app.get("/reports/{report_id}")
def get_report(report_id: str) -> dict[str, Any]:
    for path in ARTIFACTS.glob("study_*.json"):
        data = json.loads(path.read_text(encoding="utf-8"))
        report = data.get("report") or {}
        if report.get("id") == report_id:
            return report
    raise HTTPException(404, "report not found")


@app.get("/scorecard")
def get_scorecard() -> dict[str, Any]:
    path = ARTIFACTS / "pew_scorecard.json"
    if not path.exists():
        raise HTTPException(404, "run pew_bench first")
    return json.loads(path.read_text(encoding="utf-8"))
