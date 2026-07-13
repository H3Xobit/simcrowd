"""Thin orchestration graph for study -> synthesis."""

from __future__ import annotations

from pathlib import Path
from typing import Any

from simcrowd.graph.state import StudyState
from simcrowd.research.compiler import load_spec
from simcrowd.research.runner import load_personas, run_study
from simcrowd.synthesis.report import build_report


def run_study_graph(spec_path: Path, panel_path: Path, seed: int = 42) -> StudyState:
    spec = load_spec(spec_path)
    personas = load_personas(panel_path)
    result = run_study(spec, personas, seed)
    report = build_report(spec, result, personas)
    return {
        "spec": spec.model_dump(),
        "panel_path": str(panel_path),
        "seed": seed,
        "result": result,
        "report": report.model_dump(),
    }


def run_from_state(state: dict[str, Any]) -> StudyState:
    return run_study_graph(
        Path(state["spec_path"]),
        Path(state["panel_path"]),
        int(state.get("seed", 42)),
    )
