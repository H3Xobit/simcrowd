"""LangGraph-shaped study state (offline-friendly)."""

from __future__ import annotations

from typing import Any, TypedDict


class StudyState(TypedDict, total=False):
    spec: dict[str, Any]
    panel_path: str
    seed: int
    result: dict[str, Any]
    report: dict[str, Any]
