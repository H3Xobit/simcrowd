"""LLM router with offline seeded respondent mode."""

from __future__ import annotations

import hashlib
import os

from simcrowd.settings import get_settings


class LLMRouter:
    def __init__(self) -> None:
        self.settings = get_settings()
        self.offline = os.getenv("SC_OFFLINE_LLM", "1") == "1" or self.settings.sc_offline_llm

    def respondent_choice(
        self,
        *,
        persona_id: str,
        question_id: str,
        options: list[str],
        seed: int,
    ) -> str:
        digest = hashlib.sha256(f"{seed}:{persona_id}:{question_id}".encode()).hexdigest()
        idx = int(digest[:8], 16) % len(options)
        return options[idx]

    def respondent_open(self, *, persona_id: str, question: str, seed: int, attrs: dict) -> str:
        hesitation = "price" if "price_sensitive" in str(attrs) else "trust"
        return (
            f"As someone in {attrs.get('region')}, my biggest hesitation is {hesitation}. "
            f"I need clear value without creepy account access. ({persona_id})"
        )
