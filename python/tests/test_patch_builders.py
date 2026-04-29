import unittest
from pathlib import Path
import sys

sys.path.insert(0, str(Path(__file__).resolve().parents[1]))

from agent_patch_builders.patch_engine import apply_patches
from agent_patch_builders.workflow_action_builders import (
    build_add_checklist_item_patches,
    build_init_event_patches,
    build_risk_check_event_patches,
)


def make_envelope():
    return {
        "id": "wf_warning_review_001",
        "version": "1.0.0",
        "state": "reviewing",
        "allowedEvents": [
            "init_event",
            "toggle_check",
            "add_checklist_item",
            "Risk_Check_Event",
            "open_detail",
        ],
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
        self.assertEqual(overview["components"][0]["props"]["items"][0]["value"], "WARN-20260428-017")
        self.assertGreater(len(review["components"][0]["props"]["items"]), 1)
        self.assertNotIn("init_event", next_envelope["allowedEvents"])

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

    def test_risk_check_event_generates_report_before_review_section(self):
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
        patches = build_risk_check_event_patches(
            envelope=initialized,
            event={
                "id": "evt_risk_1",
                "type": "Risk_Check_Event",
                "componentId": "cmp_actions",
                "timestamp": "09:40",
                "payload": {"action": "execute"},
            },
        )
        next_envelope = apply_patches(initialized, patches)
        section_ids = [section["id"] for section in next_envelope["page"]["sections"]]

        self.assertIn("sec_review_report", section_ids)
        self.assertLess(
            section_ids.index("sec_review_report"),
            section_ids.index("sec_main_review"),
        )
        report = next(
            section for section in next_envelope["page"]["sections"] if section["id"] == "sec_review_report"
        )
        self.assertIn("风险核查报告", report["components"][0]["props"]["content"])


if __name__ == "__main__":
    unittest.main()
