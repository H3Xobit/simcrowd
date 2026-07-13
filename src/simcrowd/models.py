"""Pydantic models at I/O boundaries."""

from __future__ import annotations

from enum import StrEnum
from typing import Any
from uuid import uuid4

from pydantic import BaseModel, Field


class StudyType(StrEnum):
    survey = "survey"
    interview = "interview"
    concept_test = "concept_test"


class PersonaAttributes(BaseModel):
    age: int
    age_bin: str
    income_bin: str
    education: str
    occupation: str
    region: str
    household: str
    tech_segment: str
    sex: str


class Persona(BaseModel):
    id: str
    panel_id: str
    attributes: PersonaAttributes
    backstory: str
    attitudes_seed: list[str] = Field(default_factory=list)
    weight: float = 1.0


class Question(BaseModel):
    id: str
    text: str
    type: str
    options: list[str] | None = None
    attention_check: str | None = None


class StudySpec(BaseModel):
    id: str
    type: StudyType
    title: str
    concept_id: str | None = None
    questions: list[Question]


class ResponseItem(BaseModel):
    question_id: str
    value: str
    options_order: list[str] | None = None


class PersonaResponse(BaseModel):
    persona_id: str
    answers: list[ResponseItem]
    attention_passed: bool = True
    consistency_ok: bool = True
    resampled: bool = False


class Insight(BaseModel):
    segment: str
    text: str
    persona_ids: list[str]
    count: int


class ResearchReport(BaseModel):
    id: str = Field(default_factory=lambda: str(uuid4()))
    study_id: str
    summary: str
    insights: list[Insight]
    objections: list[dict[str, Any]] = Field(default_factory=list)
    pricing: dict[str, Any] = Field(default_factory=dict)
    attention_pass_rate: float
    cost_usd: float = 0.0
    verification_ok: bool = True


class HealthResponse(BaseModel):
    status: str
    service: str = "simcrowd-api"
    version: str
