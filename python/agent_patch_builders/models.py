"""Shared Python-side models and helpers for patch generation."""

from __future__ import annotations

from dataclasses import dataclass
from typing import Any, Dict, List, Optional, TypedDict


JSONDict = Dict[str, Any]


class WorkflowMessageDict(TypedDict, total=False):
    id: str
    role: str
    title: str
    body: str
    tone: str
    timestamp: str


class WorkflowRiskSummaryDict(TypedDict):
    level: str
    summary: str
    details: List[str]


class ChecklistItemDict(TypedDict, total=False):
    id: str
    label: str
    description: str
    checked: bool


@dataclass(frozen=True)
class RuntimeEvent:
    """Normalized event payload used by Python builders."""

    id: str
    type: str
    component_id: str
    timestamp: str
    payload: Optional[JSONDict] = None

    @classmethod
    def from_dict(cls, data: JSONDict) -> "RuntimeEvent":
        return cls(
            id=str(data["id"]),
            type=str(data["type"]),
            component_id=str(data["componentId"]),
            timestamp=str(data["timestamp"]),
            payload=data.get("payload"),
        )


def clone(data: Any) -> Any:
    """Cheap recursive clone for JSON-like data."""

    if isinstance(data, dict):
        return {key: clone(value) for key, value in data.items()}
    if isinstance(data, list):
        return [clone(item) for item in data]
    return data
