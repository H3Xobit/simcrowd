"""Eval harness: panel realism, consistency, faithfulness, Pew smoke, reproducibility."""

from __future__ import annotations

import argparse
import json
import time
from datetime import UTC, datetime
from pathlib import Path

from simcrowd.panel.persona_writer import write_persona
from simcrowd.panel.sampler import (
    load_records,
    marginals,
    max_marginal_error,
    panel_marginals,
    to_attributes,
    weighted_sample,
)
from simcrowd.research.compiler import load_spec
from simcrowd.research.runner import run_study
from simcrowd.synthesis.report import build_report
from simcrowd.validation.pew_bench import load_topline, run_panel_pew, scorecard


def _panel(n: int, seed: int, out: Path) -> list:
    records = load_records(Path("data/census/sample.jsonl"))
    drawn = weighted_sample(records, n, seed)
    personas = []
    out.parent.mkdir(parents=True, exist_ok=True)
    with out.open("w", encoding="utf-8") as f:
        for i, rec in enumerate(drawn, start=1):
            p = write_persona(
                panel_id=f"eval_{seed}_{n}",
                idx=i,
                attributes=to_attributes(rec),
                weight=float(rec["weight"]),
            )
            personas.append(p)
            f.write(p.model_dump_json() + "\n")
    return personas, drawn, records


def run(smoke_n: int = 20) -> dict:
    t0 = time.time()
    panel_path = Path("artifacts/eval_panel.jsonl")
    personas, drawn, records = _panel(smoke_n, seed=42, out=panel_path)

    keys = ["education", "income_bin", "region", "age_bin"]
    pop = {k: marginals(records, k) for k in keys}
    # Realism gate is defined at n=200; smoke studies may use a smaller panel.
    realism_draw = drawn if smoke_n >= 200 else weighted_sample(records, 200, seed=42)
    max_err = max(max_marginal_error(pop[k], panel_marginals(realism_draw, k)) for k in keys)

    spec = load_spec(Path("data/concepts/fintech_survey.json"))
    a = run_study(spec, personas, seed=42)
    b = run_study(spec, personas, seed=42)
    report = build_report(spec, a, personas)

    truth = {}
    truth.update(load_topline(Path("data/pew/tech_adoption_topline.csv")))
    truth.update(load_topline(Path("data/pew/consumer_attitudes_topline.csv")))
    # smoke: first 4 questions only
    synth = run_panel_pew(panel_path, seed=42)
    truth4 = {k: truth[k] for k in list(truth)[:4] if k in truth}
    card = scorecard(synth, truth4)

    result = {
        "timestamp": datetime.now(tz=UTC).isoformat(),
        "n": smoke_n,
        "panel_max_marginal_error": round(max_err, 4),
        "consistency_rate": a["consistency_rate"],
        "attention_pass_rate": a["attention_pass_rate"],
        "report_verification_ok": report.verification_ok,
        "reproducible": a["responses"] == b["responses"],
        "pew_mean_mae": card["mean_mae"],
        "pew_directional_agreement_rate": card["directional_agreement_rate"],
        "cost_per_study_usd": a["cost_usd"],
        "latency_s": round(time.time() - t0, 3),
    }
    return result


def main() -> None:
    parser = argparse.ArgumentParser()
    parser.add_argument("--smoke", type=int, default=20)
    parser.add_argument("--full", action="store_true")
    args = parser.parse_args()
    n = 200 if args.full else args.smoke
    result = run(smoke_n=n)
    out_dir = Path("evals/results")
    out_dir.mkdir(parents=True, exist_ok=True)
    stamp = datetime.now(tz=UTC).strftime("%Y%m%dT%H%M%SZ")
    path = out_dir / f"{stamp}.json"
    path.write_text(json.dumps(result, indent=2), encoding="utf-8")
    mirror = Path("web/public/evals/latest.json")
    if mirror.parent.exists() or True:
        mirror.parent.mkdir(parents=True, exist_ok=True)
        mirror.write_text(json.dumps(result, indent=2), encoding="utf-8")
    print(json.dumps(result, indent=2))
    if result["consistency_rate"] < 0.9:
        raise SystemExit("consistency_rate below 0.9")
    if not result["report_verification_ok"]:
        raise SystemExit("report verification failed")
    if not result["reproducible"]:
        raise SystemExit("reproducibility check failed")


if __name__ == "__main__":
    main()
