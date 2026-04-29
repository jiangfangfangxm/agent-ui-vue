"""Section builders for the warning review workspace."""

from __future__ import annotations

from typing import Dict, Iterable, List

from .models import ChecklistItemDict


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
