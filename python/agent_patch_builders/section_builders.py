"""Section builders for the warning review workspace."""

from __future__ import annotations

from typing import Dict, Iterable, List, Literal, Optional

from .models import ChecklistItemDict

RiskDecision = Optional[Literal["has_risk", "no_risk"]]


def build_warning_detail_section(detail_items: List[Dict[str, str]]) -> Dict[str, object]:
    return {
        "id": "sec_overview",
        "title": "预警情况详情",
        "description": "该区域内容由初始化事件触发后，通过服务端 patch 回填。",
        "components": [
            {
                "id": "cmp_warning_detail",
                "type": "key_value",
                "props": {
                    "layout": "grid",
                    "columns": 3,
                    "minColumnWidth": 220,
                    "items": detail_items,
                },
            }
        ],
    }


def build_review_direction_section(items: Iterable[ChecklistItemDict]) -> Dict[str, object]:
    return {
        "id": "sec_main_review",
        "title": "核查方向",
        "description": "由服务端返回的核查建议与人工补充方向组成。",
        "components": [
            {
                "id": "cmp_checklist",
                "type": "checklist",
                "props": {
                    "action": {"eventType": "toggle_check"},
                    "items": list(items),
                },
            },
            {
                "id": "cmp_custom_check_input",
                "type": "text_input",
                "props": {
                    "eventType": "add_checklist_item",
                    "label": "新增核查方向",
                    "placeholder": "例如：核验交易对手与受益人是否存在隐性关联",
                    "buttonLabel": "添加到清单",
                    "helperText": "输入后会由运行时生成 patch，并把新的核查方向回写到当前 checklist。",
                    "clearOnSubmit": True,
                },
            },
            {
                "id": "cmp_actions",
                "type": "button_group",
                "props": {
                    "actions": [
                        {
                            "label": "执行核查",
                            "eventType": "Risk_Check_Event",
                            "payload": {"action": "execute"},
                            "buttonType": "primary",
                        }
                    ]
                },
            },
        ],
    }


def build_risk_check_report_section(report_text: str) -> Dict[str, object]:
    return {
        "id": "sec_review_report",
        "title": "核查报告",
        "description": "由 Risk_Check_Event 触发后返回的核查报告。",
        "components": [
            {
                "id": "cmp_review_report",
                "type": "text",
                "props": {
                    "content": report_text,
                    "variant": "body",
                },
            }
        ],
    }


def build_report_actions_section() -> Dict[str, object]:
    return {
        "id": "sec_report_actions",
        "title": "报告后续处理",
        "description": "核查报告生成后，可继续修改报告、补充核查方向，或进入风险认定环节。",
        "components": [
            {
                "id": "cmp_report_actions",
                "type": "button_group",
                "props": {
                    "actions": [
                        {
                            "label": "修改核查报告",
                            "eventType": "edit_report",
                            "buttonType": "warning",
                        },
                        {
                            "label": "新增核查方向",
                            "eventType": "add_review_direction_after_report",
                            "buttonType": "primary",
                        },
                        {
                            "label": "进入风险认定环节",
                            "eventType": "enter_risk_identification",
                            "buttonType": "success",
                        },
                    ]
                },
            }
        ],
    }


def build_add_review_direction_section() -> Dict[str, object]:
    return {
        "id": "sec_add_review_direction",
        "title": "新增核查方向",
        "description": "请输入新的核查方向，确认后系统会更新核查方向清单，并重新生成核查报告。",
        "components": [
            {
                "id": "cmp_add_review_direction_input",
                "type": "text_input",
                "props": {
                    "eventType": "submit_new_direction_after_report",
                    "label": "新核查方向",
                    "placeholder": "例如：联系客户补充交易背景说明并核验资金用途",
                    "buttonLabel": "确认并重新风险核查",
                    "helperText": "确认后会回写到“核查方向”清单，并重新生成核查报告。",
                    "clearOnSubmit": True,
                },
            },
            {
                "id": "cmp_add_review_direction_cancel",
                "type": "button_group",
                "props": {
                    "actions": [
                        {
                            "label": "取消新增核查方向",
                            "eventType": "cancel_add_direction",
                            "buttonType": "info",
                        }
                    ]
                },
            },
        ],
    }


def _decision_label(decision: RiskDecision) -> str:
    if decision == "has_risk":
        return "有风险"
    if decision == "no_risk":
        return "无风险"
    return "未选择"


def build_risk_identification_section(
    *,
    decision: RiskDecision,
    reason: str,
) -> Dict[str, object]:
    components: List[Dict[str, object]] = [
        {
            "id": "cmp_risk_identification_state",
            "type": "key_value",
            "props": {
                "items": [
                    {"label": "当前风险结论", "value": _decision_label(decision)},
                    {"label": "风险认定说明", "value": reason or "未填写"},
                ]
            },
        },
        {
            "id": "cmp_risk_identification_hint",
            "type": "text",
            "props": {
                "content": "请先选择“有风险”或“无风险”，再补充风险认定说明。",
                "variant": "caption",
            },
        },
        {
            "id": "cmp_risk_identification_actions",
            "type": "button_group",
            "props": {
                "actions": [
                    {
                        "label": "有风险",
                        "eventType": "set_risk_decision",
                        "payload": {"decision": "has_risk"},
                        "buttonType": "danger",
                    },
                    {
                        "label": "无风险",
                        "eventType": "set_risk_decision",
                        "payload": {"decision": "no_risk"},
                        "buttonType": "success",
                    },
                ]
            },
        },
    ]

    if decision == "no_risk":
        components.append(
            {
                "id": "cmp_risk_identification_confirm",
                "type": "button_group",
                "props": {
                    "actions": [
                        {
                            "label": "确认无风险并解警",
                            "eventType": "resolve_no_risk",
                            "buttonType": "success",
                        }
                    ]
                },
            }
        )
    components.append(
        {
            "id": "cmp_risk_reason_input",
            "type": "text_input",
            "props": {
                "eventType": "update_risk_reason",
                "label": "风险认定说明",
                "placeholder": "请输入本次风险认定的依据与说明",
                "buttonLabel": "保存说明",
                "helperText": "保存后会通过 patch 回写到当前风险认定区。",
                "clearOnSubmit": True,
            },
        }
    )

    if decision == "has_risk":
        components.append(
            {
                "id": "cmp_risk_identification_hint_has_risk",
                "type": "text",
                "props": {
                    "content": "已选择“有风险”，系统将自动展开行动计划区域。你仍可继续补充风险认定说明。",
                    "variant": "caption",
                },
            }
        )

    return {
        "id": "sec_risk_identification",
        "title": "风险认定",
        "description": "请先确认是否存在风险，并补充风险认定说明。",
        "components": components,
    }


def build_action_plan_section(
    *,
    items: Iterable[ChecklistItemDict],
    reason: str,
) -> Dict[str, object]:
    materialized_items = list(items)
    checked_count = sum(1 for item in materialized_items if item.get("checked"))
    item_labels = "、".join(str(item.get("label", "")) for item in materialized_items)

    return {
        "id": "sec_action_plan",
        "title": "行动计划",
        "description": "已确认存在风险，请从推荐行动中选择，或补充新的行动事项。",
        "components": [
            {
                "id": f"cmp_action_plan_checklist_{len(materialized_items)}_{checked_count}",
                "type": "checklist",
                "props": {
                    "action": {"eventType": "toggle_action_item"},
                    "items": materialized_items,
                },
            },
            {
                "id": "cmp_action_plan_input",
                "type": "text_input",
                "props": {
                    "eventType": "add_action_item",
                    "label": "新增行动事项",
                    "placeholder": "例如：联系客户补充交易背景材料并限时回传",
                    "buttonLabel": "添加行动事项",
                    "helperText": "新增后会回写到当前行动计划清单中。",
                    "clearOnSubmit": True,
                },
            },
            {
                "id": "cmp_action_plan_confirm",
                "type": "button_group",
                "props": {
                    "actions": [
                        {
                            "label": "确认行动计划",
                            "eventType": "confirm_action_plan",
                            "buttonType": "primary",
                        }
                    ]
                },
            },
            {
                "id": "cmp_action_plan_intro",
                "type": "text",
                "props": {
                    "content": (
                        "当前风险认定结果为“有风险”。\n"
                        f"风险认定说明：{reason or '未填写'}\n"
                        f"当前行动事项数：{len(materialized_items)}（已选 {checked_count} 项）\n"
                        f"当前行动事项：{item_labels or '暂无'}\n\n"
                        "请勾选推荐行动，或新增行动事项后再确认行动计划。"
                    ),
                    "variant": "caption",
                },
            },
        ],
    }


def build_no_risk_resolution_section(reason: str) -> Dict[str, object]:
    return {
        "id": "sec_resolution_result_no_risk",
        "title": "处置结果",
        "description": "该预警已完成无风险解警处理。",
        "components": [
            {
                "id": "cmp_resolution_result_no_risk",
                "type": "result_summary",
                "props": {
                    "status": "success",
                    "headline": "已解警",
                    "summary": "本次风险认定结果为无风险，系统已完成解警处理。",
                    "nextSteps": [
                        "保留本次核查与风险认定说明作为审计依据。",
                        f"风险认定说明：{reason or '未填写'}",
                    ],
                },
            }
        ],
    }


def build_action_resolution_section(
    *,
    reason: str,
    actions: List[str],
) -> Dict[str, object]:
    return {
        "id": "sec_resolution_result_with_action",
        "title": "处置结果",
        "description": "该预警已完成风险认定，并确认后续行动计划。",
        "components": [
            {
                "id": "cmp_resolution_result_with_action",
                "type": "result_summary",
                "props": {
                    "status": "warning",
                    "headline": "行动计划已确认",
                    "summary": "本次风险认定结果为有风险，预警核查任务已转入行动执行阶段。",
                    "nextSteps": [
                        f"风险认定说明：{reason or '未填写'}",
                        *actions,
                    ],
                },
            }
        ],
    }
