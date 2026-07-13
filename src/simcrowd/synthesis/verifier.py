"""Recompute cited counts from raw responses; flag mismatches."""

from __future__ import annotations

from typing import Any

from simcrowd.models import Persona, ResearchReport


def verify_counts(
    report: ResearchReport,
    study: dict[str, Any],
    personas_by_id: dict[str, Persona],
) -> bool:
    responses = {r["persona_id"]: r for r in study["responses"]}
    for insight in report.insights:
        hot = 0
        for pid in insight.persona_ids:
            if pid not in responses:
                return False
            rr = responses[pid]
            val = next(a["value"] for a in rr["answers"] if a["question_id"] == "q_interest")
            if val in {"Very", "Extremely"}:
                hot += 1
        # count is hot among cited persona_ids prefix list only when insight uses same definition
        # Recompute against full segment sizes encoded in text "X of Y"
        if " of " in insight.text:
            # trust count field vs recomputation over persona_ids list
            if insight.count != hot:
                return False
        if insight.count != hot:
            return False
    return True
