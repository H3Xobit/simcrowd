"""CLI to run a study spec against a persona panel."""

from __future__ import annotations

import argparse
import json
from pathlib import Path

from simcrowd.research.compiler import load_spec
from simcrowd.research.runner import load_personas, run_study, save_study
from simcrowd.settings import get_settings
from simcrowd.synthesis.report import build_report


def main() -> None:
    parser = argparse.ArgumentParser()
    parser.add_argument("--spec", type=Path, required=True)
    parser.add_argument("--panel", type=Path, required=True)
    parser.add_argument("--out", type=Path, default=Path("artifacts/study.json"))
    parser.add_argument("--seed", type=int, default=None)
    args = parser.parse_args()
    settings = get_settings()
    seed = settings.sc_seed if args.seed is None else args.seed
    spec = load_spec(args.spec)
    personas = load_personas(args.panel)
    result = run_study(spec, personas, seed)
    report = build_report(spec, result, personas)
    result["report"] = report.model_dump()
    save_study(result, args.out)
    print(json.dumps({
        "study_id": result["study_id"],
        "n": result["n"],
        "attention_pass_rate": result["attention_pass_rate"],
        "consistency_rate": result["consistency_rate"],
        "cost_usd": result["cost_usd"],
        "report_id": report.id,
        "out": str(args.out),
    }))


if __name__ == "__main__":
    main()
