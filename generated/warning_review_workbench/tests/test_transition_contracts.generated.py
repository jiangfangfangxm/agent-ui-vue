"""AUTO-GENERATED transition contract skeleton from app DSL."""

# This file is generated as a contract artifact. It intentionally does not
# import the live runtime yet; the next compiler phase will bind these
# contracts to generated handlers or the project patch service.

APP_ID = 'warning_review_workbench'

REQUIRED_PATHS = [
    {'name': 'review_to_report', 'events': ['init_event', 'Risk_Check_Event'], 'expectedState': 'report_reviewing', 'expectedSections': {'present': ['sec_review_report', 'sec_report_actions'], 'absent': ['sec_report_edit', 'sec_risk_identification', 'sec_action_plan']}},
    {'name': 'report_revision', 'events': ['init_event', 'Risk_Check_Event', 'edit_report', 'save_report_revision'], 'expectedState': 'report_reviewing', 'expectedSections': {'present': ['sec_review_report', 'sec_report_actions'], 'absent': ['sec_report_edit']}},
    {'name': 'no_risk_resolution', 'events': ['init_event', 'Risk_Check_Event', 'enter_risk_identification', 'set_risk_decision:no_risk', 'update_risk_reason', 'resolve_no_risk'], 'expectedState': 'resolved_no_risk', 'expectedSections': {'present': ['sec_resolution_result_no_risk'], 'absent': ['sec_risk_identification', 'sec_action_plan']}},
    {'name': 'has_risk_action_plan', 'events': ['init_event', 'Risk_Check_Event', 'enter_risk_identification', 'set_risk_decision:has_risk', 'add_action_item', 'confirm_action_plan'], 'expectedState': 'resolved_with_action', 'expectedSections': {'present': ['sec_resolution_result_with_action'], 'absent': ['sec_action_plan']}},
]


def test_generated_contracts_are_present():
    assert REQUIRED_PATHS
    for path in REQUIRED_PATHS:
        assert path.get('name')
        assert path.get('events')
        assert path.get('expectedState')
