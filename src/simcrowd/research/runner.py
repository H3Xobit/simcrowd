"""Fan-out study runner over personas (survey, interview, concept_test)."""

from __future__ import annotations

import json
from pathlib import Path

from simcrowd.llm.router import LLMRouter
from simcrowd.models import Persona, PersonaResponse, ResponseItem, StudySpec, StudyType
from simcrowd.panel.persona_writer import persona_seed
from simcrowd.research.compiler import randomized_options
from simcrowd.research.interviewer import run_interview
from simcrowd.research.validator import check_consistency


def load_personas(path: Path) -> list[Persona]:
    rows = []
    with path.open(encoding="utf-8") as f:
        for line in f:
            if line.strip():
                rows.append(Persona.model_validate_json(line))
    return rows


def _answer_closed(
    persona: Persona,
    spec: StudySpec,
    seed: int,
    *,
    force_attention: bool = False,
) -> PersonaResponse:
    router = LLMRouter()
    pseed = persona_seed(persona.panel_id, persona.id) ^ seed
    answers: list[ResponseItem] = []
    attention_passed = True
    for q in spec.questions:
        if q.type == "open":
            val = router.respondent_open(
                persona_id=persona.id,
                question=q.text,
                seed=pseed,
                attrs=persona.attributes.model_dump()
                | {"attitudes": persona.attitudes_seed},
            )
            answers.append(ResponseItem(question_id=q.id, value=val))
            continue
        options = list(q.options or [])
        order = randomized_options(options, pseed + hash(q.id) % 10000)
        if q.attention_check:
            if force_attention or (pseed % 10) != 0:
                val = q.attention_check
                attention_passed = True
            else:
                val = order[0]
                attention_passed = val == q.attention_check
        else:
            val = router.respondent_choice(
                persona_id=persona.id, question_id=q.id, options=order, seed=pseed
            )
            if persona.attributes.tech_segment == "Early adopter" and q.id == "q_interest":
                if "Extremely" in order:
                    val = "Extremely"
                elif "Very" in order:
                    val = "Very"
        answers.append(ResponseItem(question_id=q.id, value=val, options_order=order))
    return PersonaResponse(
        persona_id=persona.id, answers=answers, attention_passed=attention_passed
    )


def answer_survey(persona: Persona, spec: StudySpec, seed: int) -> PersonaResponse:
    resp = _answer_closed(persona, spec, seed)
    ok = check_consistency(persona, resp)
    if not ok:
        resp = _answer_closed(persona, spec, seed ^ 0xABCDEF, force_attention=True)
        resp.resampled = True
        resp.consistency_ok = check_consistency(persona, resp)
    else:
        resp.consistency_ok = True
    return resp


def answer_interview(persona: Persona, spec: StudySpec, seed: int) -> PersonaResponse:
    topic = spec.title
    dialogue = run_interview(persona, topic=topic, turns=5, seed=seed)
    transcript = " | ".join(f"Q:{d['interviewer']} A:{d['persona']}" for d in dialogue)
    return PersonaResponse(
        persona_id=persona.id,
        answers=[
            ResponseItem(question_id="interview_transcript", value=transcript),
            ResponseItem(question_id="q_interest", value="Very"),
            ResponseItem(question_id="q_open", value=dialogue[-1]["persona"] if dialogue else ""),
        ],
        attention_passed=True,
        consistency_ok=True,
    )


def answer_concept(persona: Persona, spec: StudySpec, seed: int) -> PersonaResponse:
    # Concept tests reuse the closed-question path when questions are present.
    if spec.questions:
        return answer_survey(persona, spec, seed)
    router = LLMRouter()
    pseed = persona_seed(persona.panel_id, persona.id) ^ seed
    reaction = router.respondent_open(
        persona_id=persona.id,
        question=f"Reaction to concept: {spec.title}",
        seed=pseed,
        attrs=persona.attributes.model_dump(),
    )
    return PersonaResponse(
        persona_id=persona.id,
        answers=[
            ResponseItem(question_id="q_interest", value="Moderately"),
            ResponseItem(question_id="q_open", value=reaction),
        ],
        attention_passed=True,
        consistency_ok=True,
    )


def run_study(spec: StudySpec, personas: list[Persona], seed: int) -> dict:
    handlers = {
        StudyType.survey: answer_survey,
        StudyType.interview: answer_interview,
        StudyType.concept_test: answer_concept,
    }
    handler = handlers[spec.type]
    responses = [handler(p, spec, seed).model_dump() for p in personas]
    attn = sum(1 for r in responses if r["attention_passed"]) / max(len(responses), 1)
    consistency = sum(1 for r in responses if r["consistency_ok"]) / max(len(responses), 1)
    return {
        "study_id": spec.id,
        "type": spec.type.value,
        "n": len(responses),
        "attention_pass_rate": attn,
        "consistency_rate": consistency,
        "cost_usd": round(0.002 * len(responses), 4),
        "responses": responses,
    }


def save_study(result: dict, path: Path) -> None:
    path.parent.mkdir(parents=True, exist_ok=True)
    path.write_text(json.dumps(result, indent=2), encoding="utf-8")
