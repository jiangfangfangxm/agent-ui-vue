import sys
import unittest
from pathlib import Path

sys.path.insert(0, str(Path(__file__).resolve().parents[1]))

from agent_patch_builders.patch_engine import apply_patches
from agent_patch_builders.workflow_action_builders import (
    build_add_action_item_patches,
    build_add_checklist_item_patches,
    build_add_review_direction_after_report_patches,
    build_cancel_add_direction_patches,
    build_confirm_action_plan_patches,
    build_enter_risk_identification_patches,
    build_init_event_patches,
    build_resolve_no_risk_patches,
    build_risk_check_event_patches,
    build_set_risk_decision_patches,
    build_submit_new_direction_after_report_patches,
    build_toggle_action_item_patches,
    build_update_risk_reason_patches,
)


def make_envelope():
    return {
        "id": "wf_warning_review_001",
        "version": "1.0.0",
        "state": "reviewing",
        "allowedEvents": ["init_event"],
        "riskSummary": {
            "level": "medium",
            "summary": "当前存在一条待核查预警。",
            "details": ["等待初始化。"],
        },
        "messages": [],
        "page": {
            "id": "page_warning_review",
            "title": "预警核查工作台",
            "description": "demo",
            "sections": [
                {
                    "id": "sec_overview",
                    "title": "预警情况详情",
                    "components": [
                        {
                            "id": "cmp_warning_detail",
                            "type": "key_value",
                            "props": {
                                "layout": "grid",
                                "columns": 3,
                                "minColumnWidth": 220,
                                "items": [
                                    {"label": "预警编号", "value": "-"},
                                    {"label": "客户名称", "value": "-"},
                                ],
                            },
                        }
                    ],
                },
                {
                    "id": "sec_main_review",
                    "title": "核查方向",
                    "components": [
                        {
                            "id": "cmp_checklist",
                            "type": "checklist",
                            "props": {
                                "action": {"eventType": "toggle_check"},
                                "items": [
                                    {
                                        "id": "item_placeholder",
                                        "label": "等待服务端返回核查建议",
                                        "checked": False,
                                    }
                                ],
                            },
                        }
                    ],
                },
            ],
        },
    }


def initialize_report_stage():
    base = make_envelope()
    initialized = apply_patches(
        base,
        build_init_event_patches(
            envelope=base,
            event={
                "id": "evt_init_1",
                "type": "init_event",
                "componentId": "system_init",
                "timestamp": "09:30",
                "payload": {},
            },
        ),
    )
    return apply_patches(
        initialized,
        build_risk_check_event_patches(
            envelope=initialized,
            event={
                "id": "evt_risk_1",
                "type": "Risk_Check_Event",
                "componentId": "cmp_actions",
                "timestamp": "09:40",
                "payload": {"action": "execute"},
            },
        ),
    )


class PatchBuilderTests(unittest.TestCase):
    def test_init_event_updates_overview_and_review_direction(self):
        envelope = make_envelope()
        patches = build_init_event_patches(
            envelope=envelope,
            event={
                "id": "evt_init_1",
                "type": "init_event",
                "componentId": "system_init",
                "timestamp": "09:30",
                "payload": {},
            },
        )
        next_envelope = apply_patches(envelope, patches)

        overview = next(
            section for section in next_envelope["page"]["sections"] if section["id"] == "sec_overview"
        )
        review = next(
            section for section in next_envelope["page"]["sections"] if section["id"] == "sec_main_review"
        )

        self.assertEqual(overview["title"], "预警情况详情")
        self.assertEqual(overview["components"][0]["props"]["items"][0]["value"], "WARN-20260428-028")
        self.assertGreater(len(review["components"][0]["props"]["items"]), 1)
        self.assertEqual(
            next_envelope["allowedEvents"],
            ["toggle_check", "add_checklist_item", "Risk_Check_Event", "open_detail"],
        )

    def test_add_checklist_item_appends_direction(self):
        envelope = apply_patches(
            make_envelope(),
            build_init_event_patches(
                envelope=make_envelope(),
                event={
                    "id": "evt_init_1",
                    "type": "init_event",
                    "componentId": "system_init",
                    "timestamp": "09:30",
                    "payload": {},
                },
            ),
        )
        patches = build_add_checklist_item_patches(
            envelope=envelope,
            event={
                "id": "evt_add_1",
                "type": "add_checklist_item",
                "componentId": "cmp_custom_check_input",
                "timestamp": "09:35",
                "payload": {"label": "补充核验最终受益人变更记录"},
            },
        )
        next_envelope = apply_patches(envelope, patches)
        review = next(
            section for section in next_envelope["page"]["sections"] if section["id"] == "sec_main_review"
        )
        labels = [item["label"] for item in review["components"][0]["props"]["items"]]
        self.assertIn("补充核验最终受益人变更记录", labels)

    def test_risk_check_event_generates_report_and_report_actions(self):
        next_envelope = initialize_report_stage()
        section_ids = [section["id"] for section in next_envelope["page"]["sections"]]

        self.assertEqual(next_envelope["state"], "report_reviewing")
        self.assertIn("sec_review_report", section_ids)
        self.assertIn("sec_report_actions", section_ids)
        self.assertLess(section_ids.index("sec_review_report"), section_ids.index("sec_main_review"))
        self.assertLess(section_ids.index("sec_report_actions"), section_ids.index("sec_main_review"))
        report = next(
            section for section in next_envelope["page"]["sections"] if section["id"] == "sec_review_report"
        )
        report_actions = next(
            section for section in next_envelope["page"]["sections"] if section["id"] == "sec_report_actions"
        )
        self.assertIn("风险核查报告", report["components"][0]["props"]["content"])
        self.assertEqual(
            [action["eventType"] for action in report_actions["components"][0]["props"]["actions"]],
            ["edit_report", "add_review_direction_after_report", "enter_risk_identification"],
        )
        self.assertEqual(
            next_envelope["allowedEvents"],
            [
                "edit_report",
                "add_review_direction_after_report",
                "enter_risk_identification",
                "open_detail",
            ],
        )

    def test_add_review_direction_after_report_updates_review_and_report(self):
        report_stage = initialize_report_stage()

        add_stage = apply_patches(
            report_stage,
            build_add_review_direction_after_report_patches(
                envelope=report_stage,
                event={
                    "id": "evt_add_review_direction_1",
                    "type": "add_review_direction_after_report",
                    "componentId": "cmp_report_actions",
                    "timestamp": "09:41",
                    "payload": {},
                },
            ),
        )

        self.assertIn(
            "sec_add_review_direction",
            [section["id"] for section in add_stage["page"]["sections"]],
        )
        self.assertEqual(
            add_stage["allowedEvents"],
            ["submit_new_direction_after_report", "cancel_add_direction", "open_detail"],
        )

        submitted = apply_patches(
            add_stage,
            build_submit_new_direction_after_report_patches(
                envelope=add_stage,
                event={
                    "id": "evt_submit_review_direction_1",
                    "type": "submit_new_direction_after_report",
                    "componentId": "cmp_add_review_direction_input",
                    "timestamp": "09:42",
                    "payload": {"label": "联系客户补充交易背景说明并核验资金用途"},
                },
            ),
        )

        review = next(
            section for section in submitted["page"]["sections"] if section["id"] == "sec_main_review"
        )
        review_labels = [item["label"] for item in review["components"][0]["props"]["items"]]
        report = next(
            section for section in submitted["page"]["sections"] if section["id"] == "sec_review_report"
        )

        self.assertIn("联系客户补充交易背景说明并核验资金用途", review_labels)
        self.assertIn("联系客户补充交易背景说明并核验资金用途", report["components"][0]["props"]["content"])
        self.assertNotIn(
            "sec_add_review_direction",
            [section["id"] for section in submitted["page"]["sections"]],
        )
        self.assertEqual(
            submitted["allowedEvents"],
            [
                "edit_report",
                "add_review_direction_after_report",
                "enter_risk_identification",
                "open_detail",
            ],
        )

        cancelled = apply_patches(
            add_stage,
            build_cancel_add_direction_patches(
                envelope=add_stage,
                event={
                    "id": "evt_cancel_review_direction_1",
                    "type": "cancel_add_direction",
                    "componentId": "cmp_add_review_direction_cancel",
                    "timestamp": "09:43",
                    "payload": {},
                },
            ),
        )
        self.assertNotIn(
            "sec_add_review_direction",
            [section["id"] for section in cancelled["page"]["sections"]],
        )

    def test_enter_risk_identification_and_resolve_no_risk(self):
        report_stage = initialize_report_stage()

        risk_stage = apply_patches(
            report_stage,
            build_enter_risk_identification_patches(
                event={
                    "id": "evt_enter_risk_1",
                    "type": "enter_risk_identification",
                    "componentId": "cmp_report_actions",
                    "timestamp": "09:41",
                    "payload": {},
                }
            ),
        )
        self.assertEqual(risk_stage["state"], "risk_identifying")
        self.assertIn("sec_risk_identification", [section["id"] for section in risk_stage["page"]["sections"]])

        with_decision = apply_patches(
            risk_stage,
            build_set_risk_decision_patches(
                envelope=risk_stage,
                event={
                    "id": "evt_decision_1",
                    "type": "set_risk_decision",
                    "componentId": "cmp_risk_identification_actions",
                    "timestamp": "09:42",
                    "payload": {"decision": "no_risk"},
                },
            ),
        )
        with_reason = apply_patches(
            with_decision,
            build_update_risk_reason_patches(
                envelope=with_decision,
                event={
                    "id": "evt_reason_1",
                    "type": "update_risk_reason",
                    "componentId": "cmp_risk_reason_input",
                    "timestamp": "09:43",
                    "payload": {"label": "结合交易背景与补充材料，判断本次预警可排除风险。"},
                },
            ),
        )
        resolved = apply_patches(
            with_reason,
            build_resolve_no_risk_patches(
                envelope=with_reason,
                event={
                    "id": "evt_resolve_1",
                    "type": "resolve_no_risk",
                    "componentId": "cmp_risk_identification_confirm",
                    "timestamp": "09:44",
                    "payload": {},
                },
            ),
        )

        self.assertEqual(resolved["state"], "resolved_no_risk")
        self.assertIn("sec_resolution_result_no_risk", [section["id"] for section in resolved["page"]["sections"]])
        self.assertNotIn("sec_risk_identification", [section["id"] for section in resolved["page"]["sections"]])
        self.assertEqual(resolved["allowedEvents"], ["open_detail"])

    def test_select_has_risk_enters_action_plan_and_completes_task(self):
        report_stage = initialize_report_stage()
        risk_stage = apply_patches(
            report_stage,
            build_enter_risk_identification_patches(
                event={
                    "id": "evt_enter_risk_2",
                    "type": "enter_risk_identification",
                    "componentId": "cmp_report_actions",
                    "timestamp": "10:01",
                    "payload": {},
                }
            ),
        )
        with_decision = apply_patches(
            risk_stage,
            build_set_risk_decision_patches(
                envelope=risk_stage,
                event={
                    "id": "evt_decision_2",
                    "type": "set_risk_decision",
                    "componentId": "cmp_risk_identification_actions",
                    "timestamp": "10:02",
                    "payload": {"decision": "has_risk"},
                },
            ),
        )
        action_stage = apply_patches(
            with_decision,
            build_update_risk_reason_patches(
                envelope=with_decision,
                event={
                    "id": "evt_reason_2",
                    "type": "update_risk_reason",
                    "componentId": "cmp_risk_reason_input",
                    "timestamp": "10:03",
                    "payload": {"label": "交易频率、对手关系和资金去向均存在明显异常，需要制定行动计划。"},
                },
            ),
        )

        section_ids = [section["id"] for section in action_stage["page"]["sections"]]
        self.assertEqual(action_stage["state"], "action_planning")
        self.assertIn("sec_action_plan", section_ids)
        self.assertEqual(
            action_stage["allowedEvents"],
            [
                "set_risk_decision",
                "update_risk_reason",
                "resolve_no_risk",
                "toggle_action_item",
                "add_action_item",
                "confirm_action_plan",
                "open_detail",
            ],
        )

        toggled = apply_patches(
            action_stage,
            build_toggle_action_item_patches(
                envelope=action_stage,
                event={
                    "id": "evt_toggle_action_1",
                    "type": "toggle_action_item",
                    "componentId": "cmp_action_plan_checklist",
                    "timestamp": "10:05",
                    "payload": {"itemId": "item_manual_review"},
                },
            ),
        )
        extended = apply_patches(
            toggled,
            build_add_action_item_patches(
                envelope=toggled,
                event={
                    "id": "evt_add_action_1",
                    "type": "add_action_item",
                    "componentId": "cmp_action_plan_input",
                    "timestamp": "10:06",
                    "payload": {"label": "联系客户补充说明并限时回传材料"},
                },
            ),
        )
        resolved = apply_patches(
            extended,
            build_confirm_action_plan_patches(
                envelope=extended,
                event={
                    "id": "evt_confirm_action_1",
                    "type": "confirm_action_plan",
                    "componentId": "cmp_action_plan_confirm",
                    "timestamp": "10:07",
                    "payload": {},
                },
            ),
        )

        self.assertEqual(resolved["state"], "resolved_with_action")
        self.assertIn("sec_resolution_result_with_action", [section["id"] for section in resolved["page"]["sections"]])
        self.assertNotIn("sec_action_plan", [section["id"] for section in resolved["page"]["sections"]])
        self.assertEqual(resolved["allowedEvents"], ["open_detail"])


if __name__ == "__main__":
    unittest.main()
