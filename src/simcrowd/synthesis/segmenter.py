"""Segment personas by attributes for insight grouping."""

from __future__ import annotations

from collections import defaultdict

from simcrowd.models import Persona


def segment_key(p: Persona) -> str:
    a = p.attributes
    return f"{a.tech_segment}|{a.income_bin}|{a.region}"


def group_personas(personas: list[Persona]) -> dict[str, list[Persona]]:
    groups: dict[str, list[Persona]] = defaultdict(list)
    for p in personas:
        groups[segment_key(p)].append(p)
    return dict(groups)
