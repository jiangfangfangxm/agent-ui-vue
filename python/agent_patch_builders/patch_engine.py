"""Python-side patch application engine for local agent tests."""

from __future__ import annotations

from typing import Any, Dict, List

from .models import clone


class PatchApplicationError(Exception):
    """Raised when a patch cannot be safely applied."""

    def __init__(self, message: str, patch: Dict[str, Any]) -> None:
        super().__init__(message)
        self.patch = patch


def _ensure_section_exists(sections: List[Dict[str, Any]], section_id: str, patch: Dict[str, Any]) -> None:
    if not any(section["id"] == section_id for section in sections):
        raise PatchApplicationError(f"未找到目标 section: {section_id}", patch)


def _ensure_section_missing(sections: List[Dict[str, Any]], section_id: str, patch: Dict[str, Any]) -> None:
    if any(section["id"] == section_id for section in sections):
        raise PatchApplicationError(f"目标 section 已存在: {section_id}", patch)


def apply_patches(envelope: Dict[str, Any], patches: List[Dict[str, Any]]) -> Dict[str, Any]:
    """Apply patches to a JSON-like envelope and return a new envelope."""

    current = clone(envelope)

    for patch in patches:
        sections = current["page"]["sections"]
        op = patch["op"]

        if op == "set_state":
            current["state"] = patch["value"]
        elif op == "replace_section":
            _ensure_section_exists(sections, patch["sectionId"], patch)
            current["page"]["sections"] = [
                patch["value"] if section["id"] == patch["sectionId"] else section
                for section in sections
            ]
        elif op == "append_section":
            section = patch["value"]
            _ensure_section_missing(sections, section["id"], patch)

            before_id = patch.get("beforeSectionId")
            if before_id:
                _ensure_section_exists(sections, before_id, patch)
                insert_index = next(
                    index for index, value in enumerate(sections) if value["id"] == before_id
                )
                current["page"]["sections"] = (
                    sections[:insert_index] + [section] + sections[insert_index:]
                )
            else:
                current["page"]["sections"] = sections + [section]
        elif op == "remove_section":
            _ensure_section_exists(sections, patch["sectionId"], patch)
            current["page"]["sections"] = [
                section for section in sections if section["id"] != patch["sectionId"]
            ]
        elif op == "prepend_message":
            current["messages"] = [patch["value"], *current["messages"]]
        elif op == "set_allowed_events":
            current["allowedEvents"] = list(dict.fromkeys(patch["value"]))
        elif op == "set_risk_summary":
            current["riskSummary"] = patch["value"]
        else:
            raise PatchApplicationError(f"不支持的 patch 操作: {op}", patch)

    return current
