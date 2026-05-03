"""Workflow definition and event contracts for the warning-review demo."""

from __future__ import annotations

from typing import Any, Callable, Dict, List, Optional


PayloadValidator = Callable[[Dict[str, Any]], bool]


def _optional_payload(_: Dict[str, Any]) -> bool:
    return True


def _has_non_empty_string(payload: Dict[str, Any], key: str) -> bool:
    value = payload.get(key)
    return isinstance(value, str) and bool(value.strip())


EVENT_CONTRACTS: Dict[str, Dict[str, Any]] = {
    "init_event": {
        "states": ["reviewing"],
        "validate_payload": _optional_payload,
    },
    "toggle_check": {
        "states": ["reviewing", "report_reviewing"],
        "validate_payload": lambda payload: _has_non_empty_string(payload, "itemId"),
    },
    "add_checklist_item": {
        "states": ["reviewing"],
        "validate_payload": lambda payload: _has_non_empty_string(payload, "label"),
    },
    "Risk_Check_Event": {
        "states": ["reviewing"],
        "validate_payload": _optional_payload,
    },
    "open_detail": {
        "states": [
            "reviewing",
            "report_reviewing",
            "risk_identifying",
            "action_planning",
            "resolved_no_risk",
            "resolved_with_action",
            "presenting_result",
            "awaiting_revision",
        ],
        "validate_payload": _optional_payload,
    },
    "edit_report": {
        "states": ["report_reviewing"],
        "validate_payload": _optional_payload,
    },
    "save_report_revision": {
        "states": ["awaiting_revision"],
        "validate_payload": lambda payload: _has_non_empty_string(payload, "label"),
    },
    "cancel_report_revision": {
        "states": ["awaiting_revision"],
        "validate_payload": _optional_payload,
    },
    "add_review_direction_after_report": {
        "states": ["report_reviewing"],
        "validate_payload": _optional_payload,
    },
    "submit_new_direction_after_report": {
        "states": ["report_reviewing"],
        "validate_payload": lambda payload: _has_non_empty_string(payload, "label"),
    },
    "cancel_add_direction": {
        "states": ["report_reviewing"],
        "validate_payload": _optional_payload,
    },
    "enter_risk_identification": {
        "states": ["report_reviewing"],
        "validate_payload": _optional_payload,
    },
    "set_risk_decision": {
        "states": ["risk_identifying", "action_planning"],
        "validate_payload": lambda payload: payload.get("decision") in {"has_risk", "no_risk"},
    },
    "update_risk_reason": {
        "states": ["risk_identifying", "action_planning"],
        "validate_payload": lambda payload: _has_non_empty_string(payload, "label"),
    },
    "resolve_no_risk": {
        "states": ["risk_identifying", "action_planning"],
        "validate_payload": _optional_payload,
    },
    "confirm_risk_identification": {
        "states": ["risk_identifying"],
        "validate_payload": _optional_payload,
    },
    "toggle_action_item": {
        "states": ["action_planning"],
        "validate_payload": lambda payload: _has_non_empty_string(payload, "itemId"),
    },
    "add_action_item": {
        "states": ["action_planning"],
        "validate_payload": lambda payload: _has_non_empty_string(payload, "label"),
    },
    "confirm_action_plan": {
        "states": ["action_planning"],
        "validate_payload": _optional_payload,
    },
}


ALLOWED_EVENTS_BY_STATE: Dict[str, List[str]] = {
    "reviewing": [
        "toggle_check",
        "add_checklist_item",
        "Risk_Check_Event",
        "open_detail",
    ],
    "report_reviewing": [
        "edit_report",
        "add_review_direction_after_report",
        "enter_risk_identification",
        "open_detail",
    ],
    "risk_identifying": [
        "set_risk_decision",
        "update_risk_reason",
        "resolve_no_risk",
        "confirm_risk_identification",
        "open_detail",
    ],
    "action_planning": [
        "toggle_action_item",
        "add_action_item",
        "confirm_action_plan",
        "open_detail",
    ],
    "resolved_no_risk": ["open_detail"],
    "resolved_with_action": ["open_detail"],
    "awaiting_revision": [
        "save_report_revision",
        "cancel_report_revision",
        "open_detail",
    ],
}


def allowed_events_for_state(
    state: str,
    *,
    mode: Optional[str] = None,
    include_risk_controls: bool = False,
) -> List[str]:
    if mode == "adding_review_direction":
        return [
            "submit_new_direction_after_report",
            "cancel_add_direction",
            "open_detail",
        ]

    events = list(ALLOWED_EVENTS_BY_STATE.get(state, ["open_detail"]))
    if state == "action_planning" and include_risk_controls:
        events = [
            "set_risk_decision",
            "update_risk_reason",
            "resolve_no_risk",
            *events,
        ]

    return list(dict.fromkeys(events))


def validate_event_contract(state: str, event: Dict[str, Any]) -> None:
    event_type = str(event.get("type", ""))
    contract = EVENT_CONTRACTS.get(event_type)
    if not contract:
        raise ValueError(f"Unsupported event type: {event_type}")

    if state not in contract["states"]:
        raise ValueError(f"Event '{event_type}' is not allowed in state '{state}'")

    validator: PayloadValidator = contract["validate_payload"]
    if not validator(event.get("payload") or {}):
        raise ValueError(f"Event '{event_type}' payload does not match its contract")
