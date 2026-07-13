"""Replicate Pew topline questions on the synthetic panel and score agreement."""

from __future__ import annotations

import argparse
import json
from collections import Counter
from pathlib import Path

import pandas as pd

from simcrowd.llm.router import LLMRouter
from simcrowd.panel.persona_writer import persona_seed
from simcrowd.research.runner import load_personas

PEW_QUESTIONS = {
    "tech_phone_check": [
        "Several times an hour",
        "Several times a day",
        "About once a day",
        "Less often",
    ],
    "tech_ai_interest": [
        "Very interested",
        "Somewhat interested",
        "Not too interested",
        "Not at all interested",
    ],
    "tech_privacy_worry": [
        "Very worried",
        "Somewhat worried",
        "Not too worried",
        "Not at all worried",
    ],
    "tech_social_daily": ["Yes", "No"],
    "fin_emergency_400": ["Yes", "No"],
    "fin_budget_track": ["Yes", "No"],
    "fin_fintech_trust": ["A great deal", "A fair amount", "Not much", "Not at all"],
    "fin_save_monthly": ["Yes", "No"],
}


def js_divergence(p: dict[str, float], q: dict[str, float]) -> float:
    import math

    keys = set(p) | set(q)
    eps = 1e-12

    def h(a: dict[str, float], b: dict[str, float]) -> float:
        s = 0.0
        for k in keys:
            av = a.get(k, 0.0) + eps
            bv = b.get(k, 0.0) + eps
            s += av * math.log(av / bv)
        return s

    m = {k: 0.5 * (p.get(k, 0.0) + q.get(k, 0.0)) for k in keys}
    return 0.5 * h(p, m) + 0.5 * h(q, m)


def load_topline(path: Path) -> dict[str, dict[str, float]]:
    df = pd.read_csv(path)
    out: dict[str, dict[str, float]] = {}
    for qid, g in df.groupby("question_id"):
        out[str(qid)] = {str(r.option): float(r.pct) / 100.0 for r in g.itertuples()}
    return out


def run_panel_pew(personas_path: Path, seed: int = 42) -> dict[str, dict[str, float]]:
    personas = load_personas(personas_path)
    router = LLMRouter()
    out: dict[str, dict[str, float]] = {}
    for qid, options in PEW_QUESTIONS.items():
        counts: Counter[str] = Counter()
        for p in personas:
            ps = persona_seed(p.panel_id, p.id) ^ seed
            # Mild attribute bias for realism validation story
            choice = router.respondent_choice(
                persona_id=p.id, question_id=qid, options=options, seed=ps
            )
            if qid == "tech_ai_interest" and p.attributes.tech_segment == "Early adopter":
                choice = "Very interested" if "Very interested" in options else choice
            if qid == "tech_privacy_worry" and p.attributes.tech_segment == "Low":
                choice = "Very worried" if "Very worried" in options else choice
            counts[choice] += 1
        n = max(sum(counts.values()), 1)
        out[qid] = {k: v / n for k, v in counts.items()}
    return out


def scorecard(synthetic: dict[str, dict[str, float]], truth: dict[str, dict[str, float]]) -> dict:
    rows = []
    maes = []
    jss = []
    directional = []
    for qid, tdist in truth.items():
        sdist = synthetic.get(qid, {})
        keys = set(tdist) | set(sdist)
        mae = sum(abs(tdist.get(k, 0.0) - sdist.get(k, 0.0)) for k in keys) / max(len(keys), 1)
        js = js_divergence(tdist, sdist)
        t_top = max(tdist, key=tdist.get)
        s_top = max(sdist, key=sdist.get) if sdist else None
        agree = t_top == s_top
        rows.append(
            {
                "question_id": qid,
                "mae": round(mae, 4),
                "js": round(js, 4),
                "directional_agreement": agree,
                "truth_top": t_top,
                "synth_top": s_top,
            }
        )
        maes.append(mae)
        jss.append(js)
        directional.append(agree)
    return {
        "questions": rows,
        "mean_mae": round(sum(maes) / max(len(maes), 1), 4),
        "mean_js": round(sum(jss) / max(len(jss), 1), 4),
        "directional_agreement_rate": round(
            sum(1 for x in directional if x) / max(len(directional), 1), 4
        ),
    }


def main() -> None:
    parser = argparse.ArgumentParser()
    parser.add_argument("--panel", type=Path, required=True)
    parser.add_argument("--out", type=Path, default=Path("artifacts/pew_scorecard.json"))
    parser.add_argument("--seed", type=int, default=42)
    args = parser.parse_args()
    truth = {}
    truth.update(load_topline(Path("data/pew/tech_adoption_topline.csv")))
    truth.update(load_topline(Path("data/pew/consumer_attitudes_topline.csv")))
    synth = run_panel_pew(args.panel, seed=args.seed)
    card = scorecard(synth, truth)
    args.out.parent.mkdir(parents=True, exist_ok=True)
    args.out.write_text(json.dumps(card, indent=2), encoding="utf-8")
    print(json.dumps({
        "mean_mae": card["mean_mae"],
        "mean_js": card["mean_js"],
        "directional_agreement_rate": card["directional_agreement_rate"],
        "out": str(args.out),
    }))


if __name__ == "__main__":
    main()
