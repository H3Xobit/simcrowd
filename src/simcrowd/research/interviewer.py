"""Multi-turn laddering interviewer (M2)."""

from __future__ import annotations

from simcrowd.models import Persona


def run_interview(persona: Persona, topic: str, turns: int = 5, seed: int = 42) -> list[dict]:
    dialogue = []
    probes = [
        f"What first reaction do you have to {topic}?",
        "Why does that matter to you?",
        "Can you tell me more about a recent time this came up?",
        "What would make you change your mind?",
        "If you had to summarize your stance in one sentence, what is it?",
    ]
    for i in range(min(turns, len(probes))):
        q = probes[i]
        a = (
            f"Given my {persona.attributes.occupation} role and "
            f"{persona.attributes.tech_segment} tech habits, {topic} feels "
            f"{'promising' if persona.attributes.tech_segment == 'Early adopter' else 'risky'}. "
            f"(turn {i+1})"
        )
        dialogue.append({"turn": i + 1, "interviewer": q, "persona": a})
    return dialogue
