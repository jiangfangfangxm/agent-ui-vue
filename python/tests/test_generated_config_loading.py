import sys
import unittest
from pathlib import Path

sys.path.insert(0, str(Path(__file__).resolve().parents[1]))

from agent_patch_builders.app_config_loader import load_generated_app_config
from agent_patch_builders.workflow_definition import (
    GENERATED_APP_CONFIG,
    allowed_events_for_state,
    validate_event_contract,
)


class GeneratedConfigLoadingTests(unittest.TestCase):
    def test_generated_app_config_is_available(self):
        config = load_generated_app_config()

        self.assertIsNotNone(config)
        self.assertEqual(config["app"]["id"], "warning_review_workbench")
        self.assertIn("save_report_revision", config["events"])

    def test_workflow_definition_uses_generated_allowed_events(self):
        self.assertIsNotNone(GENERATED_APP_CONFIG)
        self.assertEqual(
            allowed_events_for_state("awaiting_revision"),
            ["save_report_revision", "cancel_report_revision", "open_detail"],
        )
        self.assertEqual(
            allowed_events_for_state("report_reviewing", mode="adding_review_direction_after_report"),
            ["submit_new_direction_after_report", "cancel_add_direction", "open_detail"],
        )

    def test_generated_event_contract_validation(self):
        validate_event_contract(
            "awaiting_revision",
            {
                "id": "evt_save_report_revision",
                "type": "save_report_revision",
                "componentId": "cmp_report_revision_input",
                "timestamp": "10:00",
                "payload": {"label": "修订后的报告"},
            },
        )

        with self.assertRaises(ValueError):
            validate_event_contract(
                "awaiting_revision",
                {
                    "id": "evt_save_report_revision_invalid",
                    "type": "save_report_revision",
                    "componentId": "cmp_report_revision_input",
                    "timestamp": "10:00",
                    "payload": {"label": "   "},
                },
            )


if __name__ == "__main__":
    unittest.main()
