"""CLI: build a persona panel from ACS-like joint sample."""

from __future__ import annotations

import argparse
import json
from pathlib import Path
from uuid import uuid4

from simcrowd.panel.persona_writer import write_persona
from simcrowd.panel.sampler import load_records, to_attributes, weighted_sample
from simcrowd.settings import get_settings


def main() -> None:
    parser = argparse.ArgumentParser()
    parser.add_argument("--size", type=int, default=None)
    parser.add_argument("--seed", type=int, default=None)
    parser.add_argument("--census", type=Path, default=Path("data/census/sample.jsonl"))
    parser.add_argument("--out", type=Path, default=Path("artifacts/personas.jsonl"))
    args = parser.parse_args()
    settings = get_settings()
    size = args.size or settings.sc_panel_size
    seed = settings.sc_seed if args.seed is None else args.seed
    panel_id = f"panel_{seed}_{size}_{uuid4().hex[:8]}"
    records = load_records(args.census)
    drawn = weighted_sample(records, size, seed)
    args.out.parent.mkdir(parents=True, exist_ok=True)
    with args.out.open("w", encoding="utf-8") as f:
        for i, rec in enumerate(drawn, start=1):
            persona = write_persona(
                panel_id=panel_id,
                idx=i,
                attributes=to_attributes(rec),
                weight=float(rec["weight"]),
            )
            f.write(persona.model_dump_json() + "\n")
    meta = {"panel_id": panel_id, "size": size, "seed": seed, "path": str(args.out)}
    print(json.dumps(meta))


if __name__ == "__main__":
    main()
