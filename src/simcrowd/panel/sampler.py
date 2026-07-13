"""Weighted ACS joint-distribution sampling (whole person records)."""

from __future__ import annotations

import json
import math
from collections import defaultdict
from pathlib import Path

import numpy as np

from simcrowd.models import PersonaAttributes

# Stratify on these fields so panel equal-weight marginals track ACS within ~3pp
# while still drawing whole person records (joints preserved inside each cell).
STRATA_KEYS = ("age_bin", "region", "education", "income_bin")


def load_records(path: Path) -> list[dict]:
    rows = []
    with path.open(encoding="utf-8") as f:
        for line in f:
            line = line.strip()
            if line:
                rows.append(json.loads(line))
    if not rows:
        raise ValueError(f"no census records in {path}")
    return rows


def _cell_key(record: dict) -> tuple[str, ...]:
    return tuple(str(record[k]) for k in STRATA_KEYS)


def weighted_sample(records: list[dict], n: int, seed: int) -> list[dict]:
    """Sample whole records with PPS inside ACS-weight strata quotas.

    Quotas use the largest-remainder method on weighted cell shares so the
    resulting panel's equal-weight marginals stay close to ACS marginals.
    """
    if n <= 0:
        return []
    rng = np.random.default_rng(seed)
    pools: dict[tuple[str, ...], list[int]] = defaultdict(list)
    cell_w: dict[tuple[str, ...], float] = defaultdict(float)
    for i, rec in enumerate(records):
        key = _cell_key(rec)
        pools[key].append(i)
        cell_w[key] += float(rec["weight"])
    tot_w = sum(cell_w.values()) or 1.0
    raw = {c: n * (w / tot_w) for c, w in cell_w.items()}
    floors = {c: int(math.floor(v)) for c, v in raw.items()}
    rem = n - sum(floors.values())
    frac = sorted(((raw[c] - floors[c], c) for c in raw), reverse=True)
    quotas = floors.copy()
    for i in range(rem):
        quotas[frac[i][1]] += 1

    chosen: list[dict] = []
    for cell, q in quotas.items():
        idxs = pools[cell]
        if not idxs or q <= 0:
            continue
        weights = np.asarray([float(records[i]["weight"]) for i in idxs], dtype=np.float64)
        weights = weights / weights.sum()
        replace = q > len(idxs)
        pick = rng.choice(len(idxs), size=q, replace=replace, p=weights)
        chosen.extend(records[idxs[int(j)]] for j in pick)

    if len(chosen) < n:
        # Rare pad: global PPS fill
        weights = np.asarray([float(r["weight"]) for r in records], dtype=np.float64)
        weights = weights / weights.sum()
        need = n - len(chosen)
        fill = rng.choice(len(records), size=need, replace=True, p=weights)
        chosen.extend(records[int(i)] for i in fill)
    return chosen[:n]


def marginals(records: list[dict], key: str) -> dict[str, float]:
    tot = sum(float(r["weight"]) for r in records)
    counts: dict[str, float] = defaultdict(float)
    for r in records:
        counts[str(r[key])] += float(r["weight"])
    return {k: v / tot for k, v in counts.items()}


def panel_marginals(sample: list[dict], key: str) -> dict[str, float]:
    # equal weight within drawn panel (each persona is one respondent)
    counts: dict[str, float] = defaultdict(float)
    for r in sample:
        counts[str(r[key])] += 1.0
    n = max(len(sample), 1)
    return {k: v / n for k, v in counts.items()}


def max_marginal_error(population: dict[str, float], panel: dict[str, float]) -> float:
    keys = set(population) | set(panel)
    return max(abs(population.get(k, 0.0) - panel.get(k, 0.0)) for k in keys)


def to_attributes(record: dict) -> PersonaAttributes:
    return PersonaAttributes(
        age=int(record["age"]),
        age_bin=str(record["age_bin"]),
        income_bin=str(record["income_bin"]),
        education=str(record["education"]),
        occupation=str(record["occupation"]),
        region=str(record["region"]),
        household=str(record["household"]),
        tech_segment=str(record["tech_segment"]),
        sex=str(record["sex"]),
    )
