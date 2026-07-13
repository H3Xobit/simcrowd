"""Questionnaire compiler with option-order randomization helpers."""

from __future__ import annotations

import json
from pathlib import Path

from simcrowd.models import StudySpec


def load_spec(path: Path) -> StudySpec:
    data = json.loads(path.read_text(encoding="utf-8"))
    return StudySpec.model_validate(data)


def randomized_options(options: list[str], rng_seed: int) -> list[str]:
    import random

    opts = list(options)
    random.Random(rng_seed).shuffle(opts)
    return opts
