"""Response consistency checks against persona attributes."""

from __future__ import annotations

from simcrowd.models import Persona, PersonaResponse


def check_consistency(persona: Persona, response: PersonaResponse) -> bool:
    """Cheap heuristic: price-sensitive personas should not pick top luxury price often."""
    attrs = persona.attributes
    for ans in response.answers:
        if ans.question_id == "q_pay" and attrs.income_bin == "<35k":
            if ans.value in {"$35+", "$20"} and attrs.tech_segment == "Low":
                return False
    return True
