"""Turn attribute vectors into consistent persona backstories."""

from __future__ import annotations

import hashlib

from simcrowd.models import Persona, PersonaAttributes
from simcrowd.settings import get_settings


def persona_seed(panel_id: str, persona_id: str) -> int:
    digest = hashlib.sha256(f"{panel_id}:{persona_id}".encode()).hexdigest()
    return int(digest[:16], 16) % (2**31 - 1)


def write_persona(
    *,
    panel_id: str,
    idx: int,
    attributes: PersonaAttributes,
    weight: float,
) -> Persona:
    settings = get_settings()
    persona_id = f"P{idx:04d}"
    seed = persona_seed(panel_id, persona_id)
    # Offline deterministic backstory (LLM path reserved when keys present)
    attitudes = _attitudes(attributes, seed)
    backstory = (
        f"{attributes.sex} age {attributes.age} in the {attributes.region}, "
        f"education={attributes.education}, occupation={attributes.occupation}, "
        f"household={attributes.household}, income={attributes.income_bin}. "
        f"Tech posture: {attributes.tech_segment}. "
        f"Cares about reliability, clear pricing, and not feeling judged by apps. "
        f"Seed={seed}."
    )
    if not settings.sc_offline_llm and settings.anthropic_api_key:
        # Live path can be wired later; keep offline prose for reliability in CI.
        pass
    return Persona(
        id=persona_id,
        panel_id=panel_id,
        attributes=attributes,
        backstory=backstory,
        attitudes_seed=attitudes,
        weight=weight,
    )


def _attitudes(attrs: PersonaAttributes, seed: int) -> list[str]:
    tags = []
    if attrs.tech_segment == "Early adopter":
        tags += ["curious_about_new_tools", "tolerates_beta_edges"]
    elif attrs.tech_segment == "Low":
        tags += ["skeptical_of_apps", "prefers_human_support"]
    else:
        tags += ["practical_adopter"]
    if attrs.income_bin in {"<35k", "35-75k"}:
        tags += ["price_sensitive"]
    else:
        tags += ["quality_over_price"]
    if "Professional" in attrs.occupation or attrs.occupation == "STEM":
        tags += ["time_poor"]
    tags.append(f"seed:{seed % 997}")
    return tags
