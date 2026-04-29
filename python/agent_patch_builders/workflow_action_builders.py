"""Business-oriented patch builders for Python agents."""

from __future__ import annotations

from typing import Any, Dict, Iterable, List, Optional

from .message_builders import build_message
from .models import ChecklistItemDict, RuntimeEvent, clone
from .patch_helpers import (
    build_append_section_patch,
    build_prepend_message_patch,
    build_remove_section_patch,
    build_replace_section_patch,
    build_set_allowed_events_patch,
    build_set_risk_summary_patch,
    build_set_state_patch,
)
from .section_builders import (
    build_review_direction_section,
    build_risk_check_report_section,
    build_warning_detail_section,
)
from .summary_builders import build_risk_summary


def _find_section(envelope: Dict[str, Any], section_id: str) -> Optional[Dict[str, Any]]:
    return next(
        (section for section in envelope["page"]["sections"] if section["id"] == section_id),
        None,
    )


def _find_checklist_component(envelope: Dict[str, Any]) -> Optional[Dict[str, Any]]:
    section = _find_section(envelope, "sec_main_review")
    if not section:
        return None
    return next(
        (component for component in section["components"] if component["type"] == "checklist"),
        None,
    )


def _overview_items(envelope: Dict[str, Any]) -> List[Dict[str, str]]:
    section = _find_section(envelope, "sec_overview")
    if not section:
        return []
    component = next(
        (component for component in section["components"] if component["type"] == "key_value"),
        None,
    )
    return clone(component["props"]["items"]) if component else []


def _checked_items(envelope: Dict[str, Any]) -> List[ChecklistItemDict]:
    checklist = _find_checklist_component(envelope)
    if not checklist:
        return []
    return [item for item in checklist["props"]["items"] if item.get("checked")]


def _unchecked_items(envelope: Dict[str, Any]) -> List[ChecklistItemDict]:
    checklist = _find_checklist_component(envelope)
    if not checklist:
        return []
    return [item for item in checklist["props"]["items"] if not item.get("checked")]


def build_init_event_patches(
    *,
    envelope: Dict[str, Any],
    event: Dict[str, Any],
    warning_detail_items: Optional[List[Dict[str, str]]] = None,
    review_direction_items: Optional[Iterable[ChecklistItemDict]] = None,
) -> List[Dict[str, Any]]:
    runtime_event = RuntimeEvent.from_dict(event)
    warning_detail_items = warning_detail_items or [
        {"label": "预警编号", "value": "WARN-20260428-017"},
        {"label": "客户名称", "value": "华东星联贸易有限公司"},
        {"label": "预警类型", "value": "高频异常交易预警"},
        {"label": "命中时间", "value": "2026-04-28 09:03"},
        {"label": "风险等级", "value": "高风险"},
        {"label": "当前状态", "value": "待人工核查"},
    ]
    review_direction_items = list(review_direction_items or [
        {
            "id": "item_account_flow",
            "label": "核查近 7 日异常交易流水的真实业务背景",
            "description": "确认短时间内高频转入转出是否有真实贸易或结算依据。",
            "checked": False,
        },
        {
            "id": "item_counterparty",
            "label": "核验交易对手与受益人之间是否存在隐性关联",
            "description": "关注法人、联系电话、开户地址及历史交易网络中的重叠关系。",
            "checked": False,
        },
        {
            "id": "item_region",
            "label": "核查资金是否流向高风险地区或敏感通道",
            "description": "重点关注是否存在绕道结算、拆单转移或异常跨境路径。",
            "checked": False,
        },
        {
            "id": "item_documents",
            "label": "补充核验业务合同、发票与物流凭证的一致性",
            "description": "确认基础贸易资料是否与本次预警触发交易相匹配。",
            "checked": False,
        },
    ])

    return [
        build_replace_section_patch("sec_overview", build_warning_detail_section(warning_detail_items)),
        build_replace_section_patch("sec_main_review", build_review_direction_section(review_direction_items)),
        build_set_allowed_events_patch(
            ["toggle_check", "add_checklist_item", "Risk_Check_Event", "open_detail"]
        ),
        build_set_risk_summary_patch(
            build_risk_summary(
                "high",
                "预警详情与核查方向已初始化完成，当前预警需尽快进入人工核查。",
                [
                    "命中高频异常交易预警。",
                    "系统已回填 4 条核查建议。",
                    "当前状态为待人工核查。",
                ],
            )
        ),
        build_prepend_message_patch(
            build_message(
                message_id=f"msg_init_{runtime_event.id}",
                role="system",
                title="预警详情已初始化",
                body="服务端已返回 init_event 对应的 patch，并更新了“预警情况详情”与“核查方向”区块。",
                tone="success",
                timestamp=runtime_event.timestamp,
            )
        ),
    ]


def build_toggle_checklist_item_patches(
    *,
    envelope: Dict[str, Any],
    event: Dict[str, Any],
) -> List[Dict[str, Any]]:
    runtime_event = RuntimeEvent.from_dict(event)
    section = clone(_find_section(envelope, "sec_main_review"))
    checklist = _find_checklist_component(envelope)
    if not section or not checklist:
        return []

    item_id = str((runtime_event.payload or {}).get("itemId", ""))
    next_items = [
        {**item, "checked": not item.get("checked", False)} if item["id"] == item_id else item
        for item in checklist["props"]["items"]
    ]

    for component in section["components"]:
        if component["id"] == checklist["id"]:
            component["props"]["items"] = next_items

    checked_count = sum(1 for item in next_items if item.get("checked"))

    return [
        build_replace_section_patch("sec_main_review", section),
        build_prepend_message_patch(
            build_message(
                message_id=f"msg_toggle_{runtime_event.id}",
                role="user",
                title="核查方向已更新",
                body=f"核查人员已将清单进度更新为 {checked_count} 项已完成。",
                timestamp=runtime_event.timestamp,
            )
        ),
    ]


def build_add_checklist_item_patches(
    *,
    envelope: Dict[str, Any],
    event: Dict[str, Any],
) -> List[Dict[str, Any]]:
    runtime_event = RuntimeEvent.from_dict(event)
    normalized_label = str((runtime_event.payload or {}).get("label", "")).strip()
    section = clone(_find_section(envelope, "sec_main_review"))
    checklist = _find_checklist_component(envelope)

    if not section or not checklist or not normalized_label:
        return [
            build_prepend_message_patch(
                build_message(
                    message_id=f"msg_add_check_invalid_{runtime_event.id}",
                    role="system",
                    title="新增核查方向失败",
                    body="请输入有效的核查方向内容后再提交。",
                    tone="warning",
                    timestamp=runtime_event.timestamp,
                )
            )
        ]

    exists = any(
        item["label"].strip().lower() == normalized_label.lower()
        for item in checklist["props"]["items"]
    )
    if exists:
        return [
            build_prepend_message_patch(
                build_message(
                    message_id=f"msg_add_check_duplicate_{runtime_event.id}",
                    role="system",
                    title="核查方向已存在",
                    body=f"“{normalized_label}” 已在当前清单中，无需重复添加。",
                    tone="warning",
                    timestamp=runtime_event.timestamp,
                )
            )
        ]

    next_item = {
        "id": f"item_custom_{runtime_event.id}",
        "label": normalized_label,
        "description": "由核查人员在当前工作流中手动补充。",
        "checked": False,
    }

    for component in section["components"]:
        if component["type"] == "checklist":
            component["props"]["items"] = [*component["props"]["items"], next_item]

    current_summary = clone(envelope["riskSummary"])
    current_summary["details"] = [
        f"人工补充核查方向：{normalized_label}",
        *current_summary["details"],
    ][:5]

    return [
        build_replace_section_patch("sec_main_review", section),
        build_prepend_message_patch(
            build_message(
                message_id=f"msg_add_check_{runtime_event.id}",
                role="agent",
                title="核查方向已添加",
                body=f"已将新的核查方向“{normalized_label}”加入当前清单。",
                tone="success",
                timestamp=runtime_event.timestamp,
            )
        ),
        build_set_risk_summary_patch(current_summary),
    ]


def build_risk_check_event_patches(
    *,
    envelope: Dict[str, Any],
    event: Dict[str, Any],
    report_text: Optional[str] = None,
) -> List[Dict[str, Any]]:
    runtime_event = RuntimeEvent.from_dict(event)
    report_text = report_text or "\n".join(
        [
            "风险核查报告",
            "",
            "预警基本情况",
            *(
                [f"- {item['label']}：{item['value']}" for item in _overview_items(envelope)]
                or ["- 暂无预警详情信息"]
            ),
            "",
            "已执行核查内容",
            (
                "\n".join(f"- {item['label']}" for item in _checked_items(envelope))
                or "- 当前尚未勾选已完成的核查方向"
            ),
            "",
            "待继续关注方向",
            (
                "\n".join(f"- {item['label']}" for item in _unchecked_items(envelope))
                or "- 无待执行核查方向"
            ),
            "",
            "核查结论",
            "系统已根据当前预警详情与核查方向执行风险核查。综合现有信息判断，该客户交易行为存在较高可疑度，建议继续升级人工处置，并保留本次核查过程作为后续审计依据。",
        ]
    )

    report_section = build_risk_check_report_section(report_text)
    exists = _find_section(envelope, "sec_review_report") is not None

    patches: List[Dict[str, Any]] = [build_set_state_patch("presenting_result")]
    if exists:
        patches.append(build_remove_section_patch("sec_review_report"))
    patches.append(build_append_section_patch(report_section, before_section_id="sec_main_review"))
    patches.extend(
        [
            build_set_allowed_events_patch([]),
            build_set_risk_summary_patch(
                build_risk_summary(
                    "high",
                    "风险核查已执行完成，建议将当前预警升级进入后续处置流程。",
                    [
                        "核查报告已生成。",
                        "命中预警的关键方向已进入人工复核结论。",
                        "建议保留全部核查轨迹作为审计依据。",
                    ],
                )
            ),
            build_prepend_message_patch(
                build_message(
                    message_id=f"msg_risk_check_{runtime_event.id}",
                    role="agent",
                    title="核查报告已生成",
                    body="运行时已接收 Risk_Check_Event，并将核查结果写入报告区块。",
                    tone="success",
                    timestamp=runtime_event.timestamp,
                )
            ),
        ]
    )
    return patches


def build_open_detail_patches(
    *,
    event: Dict[str, Any],
) -> List[Dict[str, Any]]:
    runtime_event = RuntimeEvent.from_dict(event)
    payload = runtime_event.payload or {}
    case_id = str(payload.get("caseId", "-"))
    applicant = str(payload.get("applicant", "-"))
    amount = str(payload.get("amount", "-"))

    return [
        build_prepend_message_patch(
            build_message(
                message_id=f"msg_detail_{runtime_event.id}",
                role="agent",
                title="详情已展开",
                body=f"已请求查看案件 {case_id} 的详情。客户名称：{applicant}，关联金额：{amount}。后续可在这里接入真实详情抽屉或侧边面板。",
                timestamp=runtime_event.timestamp,
            )
        )
    ]
