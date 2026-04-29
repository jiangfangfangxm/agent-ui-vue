"""Low-level helpers for constructing patch dictionaries."""

from __future__ import annotations

from typing import Any, Dict, List, Optional


PatchDict = Dict[str, Any]


def build_replace_section_patch(section_id: str, section: Dict[str, Any]) -> PatchDict:
    return {"op": "replace_section", "sectionId": section_id, "value": section}


def build_append_section_patch(
    section: Dict[str, Any],
    before_section_id: Optional[str] = None,
) -> PatchDict:
    patch: PatchDict = {"op": "append_section", "value": section}
    if before_section_id:
        patch["beforeSectionId"] = before_section_id
    return patch


def build_remove_section_patch(section_id: str) -> PatchDict:
    return {"op": "remove_section", "sectionId": section_id}


def build_set_state_patch(state: str) -> PatchDict:
    return {"op": "set_state", "value": state}


def build_set_allowed_events_patch(events: List[str]) -> PatchDict:
    return {"op": "set_allowed_events", "value": events}


def build_set_risk_summary_patch(summary: Dict[str, Any]) -> PatchDict:
    return {"op": "set_risk_summary", "value": summary}


def build_prepend_message_patch(message: Dict[str, Any]) -> PatchDict:
    return {"op": "prepend_message", "value": message}
