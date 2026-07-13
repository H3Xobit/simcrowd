"""Download ACS PUMS helpers. Prefer cached sample for demos.

Uses Census API when available; otherwise keep using data/census/sample.jsonl.
Do not leave large raw downloads on shared workstations; they are gitignored.
"""

from __future__ import annotations

import argparse
import logging
from pathlib import Path

logger = logging.getLogger(__name__)


def main() -> None:
    parser = argparse.ArgumentParser()
    parser.add_argument("--out", type=Path, default=Path("data/census/raw"))
    args = parser.parse_args()
    args.out.mkdir(parents=True, exist_ok=True)
    readme = args.out / "README.md"
    readme.write_text(
        "\n".join(
            [
                "# ACS PUMS raw downloads",
                "",
                "Place Census microdata extracts here if pulling beyond the bundled sample.",
                "Bundled joint sample: `../sample.jsonl` (used by default for make demo/CI).",
                "API: https://api.census.gov (optional CENSUS_API_KEY).",
                "",
            ]
        ),
        encoding="utf-8",
    )
    logger.info("wrote %s", readme)


if __name__ == "__main__":
    logging.basicConfig(level="INFO")
    main()
