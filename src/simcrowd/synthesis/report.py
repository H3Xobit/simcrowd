"""Build verified research reports with cited persona IDs and recomputed counts."""

from __future__ import annotations

from collections import Counter
from typing import Any

from simcrowd.models import Insight, Persona, ResearchReport, StudySpec
from simcrowd.synthesis.pricing import van_westendorp
from simcrowd.synthesis.segmenter import group_personas
from simcrowd.synthesis.verifier import verify_counts


def build_report(spec: StudySpec, study: dict[str, Any], personas: list[Persona]) -> ResearchReport:
    by_id = {p.id: p for p in personas}
    responses = study["responses"]
    interest = Counter()
    vw_rows = []
    objections = Counter()
    for r in responses:
        ans = {a["question_id"]: a["value"] for a in r["answers"]}
        interest[ans.get("q_interest", "NA")] += 1
        if all(
            k in ans
            for k in ("q_vw_cheap", "q_vw_bargain", "q_vw_expensive", "q_vw_too_expensive")
        ):
            vw_rows.append(
                {
                    "cheap": ans["q_vw_cheap"],
                    "bargain": ans["q_vw_bargain"],
                    "expensive": ans["q_vw_expensive"],
                    "too_expensive": ans["q_vw_too_expensive"],
                }
            )
        open_text = ans.get("q_open", "") or ans.get("q_objection", "") or ""
        low = open_text.lower()
        if "price" in low:
            objections["price"] += 1
        if "trust" in low or "creepy" in low or "privacy" in low:
            objections["trust_privacy"] += 1

    groups = group_personas(personas)
    insights: list[Insight] = []
    for seg, members in sorted(groups.items(), key=lambda kv: -len(kv[1]))[:8]:
        ids = [m.id for m in members]
        hot = 0
        for pid in ids:
            rr = next(x for x in responses if x["persona_id"] == pid)
            interest_ans = next(
                (a["value"] for a in rr["answers"] if a["question_id"] == "q_interest"),
                None,
            )
            if interest_ans in {"Very", "Extremely"}:
                hot += 1
        insights.append(
            Insight(
                segment=seg,
                text=(
                    f"In segment {seg}, {hot} of {len(ids)} respondents lean "
                    f"very/extremely interested."
                ),
                persona_ids=ids,
                count=hot,
            )
        )

    pricing = van_westendorp(vw_rows)
    top = interest.most_common(1)[0] if interest else ("n/a", 0)
    summary = (
        f"Survey `{spec.title}` with n={study['n']}. "
        f"Attention pass rate={study['attention_pass_rate']:.2f}. "
        f"Top interest cell={top}."
    )
    report = ResearchReport(
        study_id=spec.id,
        summary=summary,
        insights=insights,
        objections=[{"theme": k, "count": v} for k, v in objections.most_common()],
        pricing=pricing,
        attention_pass_rate=float(study["attention_pass_rate"]),
        cost_usd=float(study.get("cost_usd") or 0.0),
    )
    report.verification_ok = verify_counts(report, study, by_id)
    return report
