import sys
import unittest
from pathlib import Path
from typing import Any, Dict, Iterable

sys.path.insert(0, str(Path(__file__).resolve().parent))
sys.path.insert(0, str(Path(__file__).resolve().parents[1]))

from agent_patch_builders.patch_engine import apply_patches
from agent_patch_builders.workflow_definition import allowed_events_for_state
from patch_service import build_patch_plan
from test_patch_builders import make_envelope


def section_ids(envelope: Dict[str, Any]) -> list[str]:
    return [section["id"] for section in envelope["page"]["sections"]]


def event(
    event_type: str,
    *,
    component_id: str = "contract_test",
    payload: Dict[str, Any] | None = None,
) -> Dict[str, Any]:
    return {
        "id": f"evt_contract_{event_type}",
        "type": event_type,
        "componentId": component_id,
        "timestamp": "10:00",
        "payload": payload or {},
    }


def dispatch(
    envelope: Dict[str, Any],
    event_type: str,
    *,
    component_id: str = "contract_test",
    payload: Dict[str, Any] | None = None,
) -> Dict[str, Any]:
    runtime_event = event(event_type, component_id=component_id, payload=payload)
    plan = build_patch_plan({"envelope": envelope, "event": runtime_event})
    return apply_patches(envelope, plan["patches"])


def assert_sections(
    test_case: unittest.TestCase,
    envelope: Dict[str, Any],
    *,
    present: Iterable[str] = (),
    absent: Iterable[str] = (),
) -> None:
    ids = section_ids(envelope)
    for section_id in present:
        test_case.assertIn(section_id, ids)
    for section_id in absent:
        test_case.assertNotIn(section_id, ids)


class WorkflowTransitionContractTests(unittest.TestCase):
    def test_review_to_report_contract(self):
        initialized = dispatch(make_envelope(), "init_event", component_id="system_init")
        self.assertEqual(initialized["state"], "reviewing")
        self.assertEqual(initialized["allowedEvents"], allowed_events_for_state("reviewing"))
        assert_sections(
            self,
            initialized,
            present=["sec_overview", "sec_main_review"],
            absent=["sec_review_report", "sec_report_actions"],
        )

        report_stage = dispatch(
            initialized,
            "Risk_Check_Event",
            component_id="cmp_actions",
            payload={"action": "execute"},
        )
        self.assertEqual(report_stage["state"], "report_reviewing")
        self.assertEqual(report_stage["allowedEvents"], allowed_events_for_state("report_reviewing"))
        assert_sections(
            self,
            report_stage,
            present=["sec_review_report", "sec_report_actions", "sec_main_review"],
            absent=["sec_report_edit", "sec_risk_identification", "sec_action_plan"],
        )
        self.assertTrue(report_stage["context"]["reportText"])

    def test_report_revision_subflow_contract(self):
        report_stage = dispatch(
            dispatch(make_envelope(), "init_event", component_id="system_init"),
            "Risk_Check_Event",
            component_id="cmp_actions",
            payload={"action": "execute"},
        )

        editing = dispatch(report_stage, "edit_report", component_id="cmp_report_actions")
        self.assertEqual(editing["state"], "awaiting_revision")
        self.assertEqual(editing["allowedEvents"], allowed_events_for_state("awaiting_revision"))
        assert_sections(
            self,
            editing,
            present=["sec_review_report", "sec_report_edit"],
            absent=["sec_report_actions", "sec_risk_identification"],
        )

        saved = dispatch(
            editing,
            "save_report_revision",
            component_id="cmp_report_revision_input",
            payload={"label": "contract revised report"},
        )
        self.assertEqual(saved["state"], "report_reviewing")
        self.assertEqual(saved["allowedEvents"], allowed_events_for_state("report_reviewing"))
        self.assertEqual(saved["context"]["reportText"], "contract revised report")
        assert_sections(
            self,
            saved,
            present=["sec_review_report", "sec_report_actions"],
            absent=["sec_report_edit"],
        )

    def test_report_add_direction_subflow_contract(self):
        report_stage = dispatch(
            dispatch(make_envelope(), "init_event", component_id="system_init"),
            "Risk_Check_Event",
            component_id="cmp_actions",
            payload={"action": "execute"},
        )

        adding = dispatch(
            report_stage,
            "add_review_direction_after_report",
            component_id="cmp_report_actions",
        )
        self.assertEqual(adding["state"], "report_reviewing")
        self.assertEqual(
            adding["allowedEvents"],
            allowed_events_for_state("report_reviewing", mode="adding_review_direction"),
        )
        assert_sections(self, adding, present=["sec_add_review_direction"], absent=["sec_risk_identification"])

        submitted = dispatch(
            adding,
            "submit_new_direction_after_report",
            component_id="cmp_add_review_direction_input",
            payload={"label": "contract extra direction"},
        )
        self.assertEqual(submitted["state"], "report_reviewing")
        self.assertEqual(submitted["allowedEvents"], allowed_events_for_state("report_reviewing"))
        self.assertIn(
            "contract extra direction",
            [item["label"] for item in submitted["context"]["reviewDirections"]],
        )
        assert_sections(
            self,
            submitted,
            present=["sec_review_report", "sec_report_actions"],
            absent=["sec_add_review_direction"],
        )

    def test_no_risk_resolution_contract(self):
        report_stage = dispatch(
            dispatch(make_envelope(), "init_event", component_id="system_init"),
            "Risk_Check_Event",
            component_id="cmp_actions",
            payload={"action": "execute"},
        )
        risk_stage = dispatch(
            report_stage,
            "enter_risk_identification",
            component_id="cmp_report_actions",
        )
        self.assertEqual(risk_stage["state"], "risk_identifying")
        self.assertEqual(risk_stage["allowedEvents"], allowed_events_for_state("risk_identifying"))
        assert_sections(self, risk_stage, present=["sec_risk_identification"])

        decided = dispatch(
            risk_stage,
            "set_risk_decision",
            component_id="cmp_risk_identification_actions",
            payload={"decision": "no_risk"},
        )
        reasoned = dispatch(
            decided,
            "update_risk_reason",
            component_id="cmp_risk_reason_input",
            payload={"label": "contract no-risk reason"},
        )
        resolved = dispatch(
            reasoned,
            "resolve_no_risk",
            component_id="cmp_risk_identification_confirm",
        )
        self.assertEqual(resolved["state"], "resolved_no_risk")
        self.assertEqual(resolved["allowedEvents"], allowed_events_for_state("resolved_no_risk"))
        self.assertEqual(resolved["context"]["riskDecision"], "no_risk")
        self.assertEqual(resolved["context"]["riskReason"], "contract no-risk reason")
        assert_sections(
            self,
            resolved,
            present=["sec_resolution_result_no_risk"],
            absent=["sec_risk_identification", "sec_action_plan", "sec_report_actions"],
        )

    def test_has_risk_action_plan_contract(self):
        report_stage = dispatch(
            dispatch(make_envelope(), "init_event", component_id="system_init"),
            "Risk_Check_Event",
            component_id="cmp_actions",
            payload={"action": "execute"},
        )
        risk_stage = dispatch(
            report_stage,
            "enter_risk_identification",
            component_id="cmp_report_actions",
        )
        action_stage = dispatch(
            risk_stage,
            "set_risk_decision",
            component_id="cmp_risk_identification_actions",
            payload={"decision": "has_risk"},
        )
        self.assertEqual(action_stage["state"], "action_planning")
        self.assertEqual(
            action_stage["allowedEvents"],
            allowed_events_for_state("action_planning", include_risk_controls=True),
        )
        self.assertEqual(action_stage["context"]["riskDecision"], "has_risk")
        assert_sections(self, action_stage, present=["sec_risk_identification", "sec_action_plan"])

        with_action = dispatch(
            action_stage,
            "add_action_item",
            component_id="cmp_action_plan_input",
            payload={"label": "contract action item"},
        )
        resolved = dispatch(
            with_action,
            "confirm_action_plan",
            component_id="cmp_action_plan_confirm",
        )
        self.assertEqual(resolved["state"], "resolved_with_action")
        self.assertEqual(resolved["allowedEvents"], allowed_events_for_state("resolved_with_action"))
        assert_sections(
            self,
            resolved,
            present=["sec_resolution_result_with_action"],
            absent=["sec_action_plan"],
        )

    def test_illegal_events_are_rejected_by_contract(self):
        report_stage = dispatch(
            dispatch(make_envelope(), "init_event", component_id="system_init"),
            "Risk_Check_Event",
            component_id="cmp_actions",
            payload={"action": "execute"},
        )
        with self.assertRaises(ValueError):
            build_patch_plan(
                {
                    "envelope": report_stage,
                    "event": event(
                        "confirm_action_plan",
                        component_id="cmp_action_plan_confirm",
                    ),
                }
            )

        editing = dispatch(report_stage, "edit_report", component_id="cmp_report_actions")
        with self.assertRaises(ValueError):
            build_patch_plan(
                {
                    "envelope": editing,
                    "event": event(
                        "save_report_revision",
                        component_id="cmp_report_revision_input",
                        payload={"label": "   "},
                    ),
                }
            )


if __name__ == "__main__":
    unittest.main()
