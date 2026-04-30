"""Business-oriented patch builders for Python agents."""

from __future__ import annotations

from typing import Any, Dict, Iterable, List, Optional

from .logging_utils import get_logger
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
    RiskDecision,
    build_action_plan_section,
    build_action_resolution_section,
    build_add_review_direction_section,
    build_no_risk_resolution_section,
    build_report_actions_section,
    build_review_direction_section,
    build_risk_check_report_section,
    build_risk_identification_section,
    build_warning_detail_section,
)
from .summary_builders import build_risk_summary

logger = get_logger("workflow_action_builders")

INIT_STAGE_ALLOWED_EVENTS = [
    "toggle_check",
    "add_checklist_item",
    "Risk_Check_Event",
    "open_detail",
]

REPORT_STAGE_ALLOWED_EVENTS = [
    "edit_report",
    "add_review_direction_after_report",
    "enter_risk_identification",
    "open_detail",
]

ADD_REVIEW_DIRECTION_ALLOWED_EVENTS = [
    "submit_new_direction_after_report",
    "cancel_add_direction",
    "open_detail",
]

RISK_IDENTIFICATION_ALLOWED_EVENTS = [
    "set_risk_decision",
    "update_risk_reason",
    "resolve_no_risk",
    "confirm_risk_identification",
    "open_detail",
]

ACTION_PLANNING_ALLOWED_EVENTS = [
    "toggle_action_item",
    "add_action_item",
    "confirm_action_plan",
    "open_detail",
]

RISK_AND_ACTION_ALLOWED_EVENTS = [
    "set_risk_decision",
    "update_risk_reason",
    "resolve_no_risk",
    "toggle_action_item",
    "add_action_item",
    "confirm_action_plan",
    "open_detail",
]


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


def _find_action_plan_checklist(envelope: Dict[str, Any]) -> Optional[Dict[str, Any]]:
    section = _find_section(envelope, "sec_action_plan")
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


def _build_risk_check_report_text(
    envelope: Dict[str, Any],
    checklist_items: Optional[List[ChecklistItemDict]] = None,
) -> str:
    items = checklist_items
    if items is None:
        checklist = _find_checklist_component(envelope)
        items = clone(checklist["props"]["items"]) if checklist else []

    checked_items = [item for item in items if item.get("checked")]
    unchecked_items = [item for item in items if not item.get("checked")]

    return "\n".join(
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
                "\n".join(f"- {item['label']}" for item in checked_items)
                or "- 当前尚未勾选已完成的核查方向"
            ),
            "",
            "待继续关注方向",
            (
                "\n".join(f"- {item['label']}" for item in unchecked_items)
                or "- 无待执行核查方向"
            ),
            "",
            "核查结论",
            "系统已根据当前预警详情与核查方向执行风险核查。综合现有信息判断，该客户交易行为存在较高可疑度，建议继续升级人工处置，并保留本次核查过程作为后续审计依据。",
        ]
    )


def _checked_action_items(envelope: Dict[str, Any]) -> List[ChecklistItemDict]:
    checklist = _find_action_plan_checklist(envelope)
    if not checklist:
        return []
    return [item for item in checklist["props"]["items"] if item.get("checked")]


def _find_risk_identification_state(envelope: Dict[str, Any]) -> tuple[RiskDecision, str]:
    section = _find_section(envelope, "sec_risk_identification")
    if not section:
        return None, ""

    key_value = next(
        (
            component
            for component in section["components"]
            if component["id"] == "cmp_risk_identification_state"
        ),
        None,
    )
    if not key_value:
        return None, ""

    items = key_value["props"]["items"]
    decision_label = next(
        (item["value"] for item in items if item["label"] == "当前风险结论"),
        "未选择",
    )
    reason = next(
        (item["value"] for item in items if item["label"] == "风险认定说明"),
        "未填写",
    )

    decision_map: Dict[str, RiskDecision] = {
        "有风险": "has_risk",
        "无风险": "no_risk",
        "未选择": None,
    }
    normalized_reason = "" if reason == "未填写" else str(reason)
    return decision_map.get(str(decision_label), None), normalized_reason


def _build_default_action_plan_items() -> List[ChecklistItemDict]:
    return [
        {
            "id": "item_freeze_monitor",
            "label": "加强账户交易监测",
            "description": "对后续资金流向与交易频率实施更严格的持续监控。",
            "checked": False,
        },
        {
            "id": "item_manual_review",
            "label": "提交人工复核审批",
            "description": "将本次预警及核查结果提交上级人工复核并保留审批意见。",
            "checked": False,
        },
        {
            "id": "item_collect_docs",
            "label": "补充收集交易背景材料",
            "description": "向客户补充索取合同、发票、物流或付款背景证明材料。",
            "checked": False,
        },
        {
            "id": "item_limit_channel",
            "label": "限制敏感通道交易",
            "description": "对高风险通道、时段或交易方式采取临时限制措施。",
            "checked": False,
        },
    ]


def _rebuild_action_plan_section(
    envelope: Dict[str, Any],
    items: List[ChecklistItemDict],
) -> Dict[str, Any]:
    _, current_reason = _find_risk_identification_state(envelope)
    return build_action_plan_section(items=items, reason=current_reason)


def build_init_event_patches(
    *,
    envelope: Dict[str, Any],
    event: Dict[str, Any],
    warning_detail_items: Optional[List[Dict[str, str]]] = None,
    review_direction_items: Optional[Iterable[ChecklistItemDict]] = None,
) -> List[Dict[str, Any]]:
    runtime_event = RuntimeEvent.from_dict(event)
    logger.info(
        "Processing init_event: event_id=%s current_allowed_events=%s",
        runtime_event.id,
        envelope.get("allowedEvents", []),
    )

    warning_detail_items = warning_detail_items or [
        {"label": "预警编号", "value": "WARN-20260428-028"},
        {"label": "客户名称", "value": "建行-华东星联贸易有限公司"},
        {"label": "预警类型", "value": "高频异常交易预警"},
        {"label": "命中时间", "value": "2026-04-28 09:03"},
        {"label": "风险等级", "value": "高风险"},
        {"label": "当前状态", "value": "待人工核查"},
    ]
    review_direction_items = list(
        review_direction_items
        or [
            {
                "id": "item_account_flow",
                "label": "核查近 7 日异常交易流水的真实业务背景",
                "description": "确认短时间内高频转入转出是否存在真实交易或结算依据。",
                "checked": False,
            },
            {
                "id": "item_counterparty",
                "label": "核验交易对手与受益人之间是否存在隐性关联",
                "description": "关注法人、联系电话、开户地址及历史交易网络中的重合关系。",
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
                "description": "确认基础交易资料是否与本次预警触发交易相匹配。",
                "checked": False,
            },
        ]
    )

    logger.debug(
        "Init payload prepared: warning_items=%s review_direction_items=%s",
        len(warning_detail_items),
        len(review_direction_items),
    )

    return [
        build_replace_section_patch(
            "sec_overview",
            build_warning_detail_section(warning_detail_items),
        ),
        build_replace_section_patch(
            "sec_main_review",
            build_review_direction_section(review_direction_items),
        ),
        build_set_allowed_events_patch(INIT_STAGE_ALLOWED_EVENTS),
        build_set_risk_summary_patch(
            build_risk_summary(
                "high",
                "预警详情与核查方向已初始化完成，当前预警需要尽快进入人工核查。",
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
                body="服务端已返回 init_event 对应的 patch，并更新了“预警情况详情”与“核查方向”区域。",
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
        logger.warning(
            "toggle_check skipped: section_or_checklist_missing event_id=%s",
            runtime_event.id,
        )
        return []

    item_id = str((runtime_event.payload or {}).get("itemId", ""))
    logger.info(
        "Processing toggle_check: event_id=%s item_id=%s",
        runtime_event.id,
        item_id,
    )

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
    logger.info(
        "Processing add_checklist_item: event_id=%s label=%s",
        runtime_event.id,
        normalized_label,
    )

    if not section or not checklist or not normalized_label:
        logger.warning(
            "add_checklist_item rejected: invalid_input event_id=%s has_section=%s has_checklist=%s",
            runtime_event.id,
            bool(section),
            bool(checklist),
        )
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
        logger.warning(
            "add_checklist_item rejected: duplicate_label event_id=%s label=%s",
            runtime_event.id,
            normalized_label,
        )
        return [
            build_prepend_message_patch(
                build_message(
                    message_id=f"msg_add_check_duplicate_{runtime_event.id}",
                    role="system",
                    title="核查方向已存在",
                    body=f"“{normalized_label}”已在当前清单中，无需重复添加。",
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
    logger.info(
        "Processing Risk_Check_Event: event_id=%s checked_items=%s unchecked_items=%s",
        runtime_event.id,
        len(_checked_items(envelope)),
        len(_unchecked_items(envelope)),
    )

    report_text = report_text or _build_risk_check_report_text(envelope)

    report_section = build_risk_check_report_section(report_text)
    report_actions_section = build_report_actions_section()
    report_exists = _find_section(envelope, "sec_review_report") is not None
    actions_exists = _find_section(envelope, "sec_report_actions") is not None
    logger.debug(
        "Risk check report prepared: event_id=%s report_exists=%s report_actions_exists=%s report_length=%s",
        runtime_event.id,
        report_exists,
        actions_exists,
        len(report_text),
    )

    patches: List[Dict[str, Any]] = [build_set_state_patch("report_reviewing")]
    if report_exists:
        patches.append(build_remove_section_patch("sec_review_report"))
    if actions_exists:
        patches.append(build_remove_section_patch("sec_report_actions"))

    patches.append(
        build_append_section_patch(report_section, before_section_id="sec_main_review")
    )
    patches.append(
        build_append_section_patch(
            report_actions_section,
            before_section_id="sec_main_review",
        )
    )
    patches.extend(
        [
            build_set_allowed_events_patch(REPORT_STAGE_ALLOWED_EVENTS),
            build_set_risk_summary_patch(
                build_risk_summary(
                    "high",
                    "风险核查已完成，请继续处理核查报告。",
                    [
                        "核查报告已生成。",
                        "后续处理选项已开放。",
                        "可继续修改报告、补充核查方向或进入风险认定。",
                    ],
                )
            ),
            build_prepend_message_patch(
                build_message(
                    message_id=f"msg_risk_check_{runtime_event.id}",
                    role="agent",
                    title="核查报告已生成",
                    body="运行时已接收 Risk_Check_Event，并在报告阶段开放了后续处理选项。",
                    tone="success",
                    timestamp=runtime_event.timestamp,
                )
            ),
        ]
    )
    return patches


def _build_report_stage_placeholder_patches(
    *,
    event: Dict[str, Any],
    title: str,
    body: str,
) -> List[Dict[str, Any]]:
    runtime_event = RuntimeEvent.from_dict(event)
    logger.info(
        "Processing report-stage placeholder action: event_type=%s event_id=%s",
        runtime_event.type,
        runtime_event.id,
    )
    return [
        build_prepend_message_patch(
            build_message(
                message_id=f"msg_{runtime_event.type}_{runtime_event.id}",
                role="system",
                title=title,
                body=body,
                tone="info",
                timestamp=runtime_event.timestamp,
            )
        )
    ]


def build_edit_report_patches(
    *,
    event: Dict[str, Any],
) -> List[Dict[str, Any]]:
    return _build_report_stage_placeholder_patches(
        event=event,
        title="修改核查报告待实现",
        body="已进入报告阶段，后续会在这里接入核查报告编辑能力。",
    )


def build_add_review_direction_after_report_patches(
    *,
    envelope: Dict[str, Any],
    event: Dict[str, Any],
) -> List[Dict[str, Any]]:
    runtime_event = RuntimeEvent.from_dict(event)
    logger.info(
        "Processing add_review_direction_after_report: event_id=%s",
        runtime_event.id,
    )

    patches: List[Dict[str, Any]] = []
    if _find_section(envelope, "sec_add_review_direction") is not None:
        patches.append(build_remove_section_patch("sec_add_review_direction"))

    patches.extend(
        [
            build_append_section_patch(
                build_add_review_direction_section(),
                before_section_id="sec_main_review",
            ),
            build_set_allowed_events_patch(ADD_REVIEW_DIRECTION_ALLOWED_EVENTS),
            build_prepend_message_patch(
                build_message(
                    message_id=f"msg_add_review_direction_open_{runtime_event.id}",
                    role="system",
                    title="新增核查方向",
                    body="请输入新的核查方向，确认后系统会更新核查方向清单，并重新生成核查报告。",
                    tone="info",
                    timestamp=runtime_event.timestamp,
                )
            ),
        ]
    )
    return patches


def build_submit_new_direction_after_report_patches(
    *,
    envelope: Dict[str, Any],
    event: Dict[str, Any],
) -> List[Dict[str, Any]]:
    runtime_event = RuntimeEvent.from_dict(event)
    normalized_label = str((runtime_event.payload or {}).get("label", "")).strip()
    section = clone(_find_section(envelope, "sec_main_review"))
    checklist = _find_checklist_component(envelope)
    logger.info(
        "Processing submit_new_direction_after_report: event_id=%s label=%s",
        runtime_event.id,
        normalized_label,
    )

    if not section or not checklist or not normalized_label:
        return [
            build_prepend_message_patch(
                build_message(
                    message_id=f"msg_submit_direction_invalid_{runtime_event.id}",
                    role="system",
                    title="新增核查方向失败",
                    body="请输入有效的核查方向内容后再提交。",
                    tone="warning",
                    timestamp=runtime_event.timestamp,
                )
            )
        ]

    current_items = clone(checklist["props"]["items"])
    exists = any(
        item["label"].strip().lower() == normalized_label.lower()
        for item in current_items
    )
    if exists:
        return [
            build_prepend_message_patch(
                build_message(
                    message_id=f"msg_submit_direction_duplicate_{runtime_event.id}",
                    role="system",
                    title="核查方向已存在",
                    body=f"“{normalized_label}”已在当前核查方向清单中，无需重复添加。",
                    tone="warning",
                    timestamp=runtime_event.timestamp,
                )
            )
        ]

    next_item = {
        "id": f"item_custom_report_{runtime_event.id}",
        "label": normalized_label,
        "description": "由核查人员在报告阶段手动补充，并重新纳入风险核查。",
        "checked": False,
    }
    next_items = [*current_items, next_item]

    for component in section["components"]:
        if component["type"] == "checklist":
            component["props"]["items"] = next_items

    report_section = build_risk_check_report_section(
        _build_risk_check_report_text(envelope, next_items)
    )
    report_actions_section = build_report_actions_section()
    current_summary = clone(envelope["riskSummary"])
    current_summary["details"] = [
        f"报告阶段补充核查方向：{normalized_label}",
        *current_summary["details"],
    ][:5]

    patches: List[Dict[str, Any]] = [
        build_replace_section_patch("sec_main_review", section),
        build_replace_section_patch("sec_review_report", report_section),
    ]
    if _find_section(envelope, "sec_report_actions") is not None:
        patches.append(build_remove_section_patch("sec_report_actions"))
    if _find_section(envelope, "sec_add_review_direction") is not None:
        patches.append(build_remove_section_patch("sec_add_review_direction"))

    patches.extend(
        [
            build_append_section_patch(
                report_actions_section,
                before_section_id="sec_main_review",
            ),
            build_set_allowed_events_patch(REPORT_STAGE_ALLOWED_EVENTS),
            build_set_risk_summary_patch(current_summary),
            build_prepend_message_patch(
                build_message(
                    message_id=f"msg_submit_direction_{runtime_event.id}",
                    role="agent",
                    title="核查方向已更新",
                    body=f"已在报告阶段新增核查方向“{normalized_label}”，并重新生成核查报告。",
                    tone="success",
                    timestamp=runtime_event.timestamp,
                )
            ),
        ]
    )
    return patches


def build_cancel_add_direction_patches(
    *,
    envelope: Dict[str, Any],
    event: Dict[str, Any],
) -> List[Dict[str, Any]]:
    runtime_event = RuntimeEvent.from_dict(event)
    logger.info(
        "Processing cancel_add_direction: event_id=%s",
        runtime_event.id,
    )

    patches: List[Dict[str, Any]] = []
    if _find_section(envelope, "sec_report_actions") is not None:
        patches.append(build_remove_section_patch("sec_report_actions"))
    if _find_section(envelope, "sec_add_review_direction") is not None:
        patches.append(build_remove_section_patch("sec_add_review_direction"))

    patches.extend(
        [
            build_append_section_patch(
                build_report_actions_section(),
                before_section_id="sec_main_review",
            ),
            build_set_allowed_events_patch(REPORT_STAGE_ALLOWED_EVENTS),
            build_prepend_message_patch(
                build_message(
                    message_id=f"msg_cancel_add_direction_{runtime_event.id}",
                    role="system",
                    title="已取消新增核查方向",
                    body="系统已返回报告阶段，你可以继续修改报告、补充核查方向或进入风险认定。",
                    tone="info",
                    timestamp=runtime_event.timestamp,
                )
            ),
        ]
    )
    return patches


def build_enter_risk_identification_patches(
    *,
    event: Dict[str, Any],
) -> List[Dict[str, Any]]:
    runtime_event = RuntimeEvent.from_dict(event)
    logger.info(
        "Processing enter_risk_identification: event_id=%s",
        runtime_event.id,
    )
    section = build_risk_identification_section(decision=None, reason="")
    return [
        build_set_state_patch("risk_identifying"),
        build_append_section_patch(section, before_section_id="sec_main_review"),
        build_set_allowed_events_patch(RISK_IDENTIFICATION_ALLOWED_EVENTS),
        build_prepend_message_patch(
            build_message(
                message_id=f"msg_enter_risk_identification_{runtime_event.id}",
                role="system",
                title="已进入风险认定环节",
                body="请先选择“有风险”或“无风险”，并补充风险认定说明。",
                tone="info",
                timestamp=runtime_event.timestamp,
            )
        ),
    ]


def build_set_risk_decision_patches(
    *,
    envelope: Dict[str, Any],
    event: Dict[str, Any],
) -> List[Dict[str, Any]]:
    runtime_event = RuntimeEvent.from_dict(event)
    _, current_reason = _find_risk_identification_state(envelope)
    decision = str((runtime_event.payload or {}).get("decision", ""))
    normalized_decision: RiskDecision = (
        "has_risk" if decision == "has_risk" else "no_risk" if decision == "no_risk" else None
    )
    logger.info(
        "Processing set_risk_decision: event_id=%s decision=%s",
        runtime_event.id,
        normalized_decision,
    )
    section = build_risk_identification_section(
        decision=normalized_decision,
        reason=current_reason,
    )
    decision_text = (
        "有风险"
        if normalized_decision == "has_risk"
        else "无风险"
        if normalized_decision == "no_risk"
        else "未选择"
    )
    patches: List[Dict[str, Any]] = [
        build_replace_section_patch("sec_risk_identification", section),
        build_prepend_message_patch(
            build_message(
                message_id=f"msg_set_risk_decision_{runtime_event.id}",
                role="system",
                title="风险结论已更新",
                body=f"当前风险结论已切换为：{decision_text}。",
                tone="info",
                timestamp=runtime_event.timestamp,
            )
        ),
    ]

    action_plan_exists = _find_section(envelope, "sec_action_plan") is not None
    if normalized_decision == "has_risk":
        action_section = build_action_plan_section(
            items=_build_default_action_plan_items(),
            reason=current_reason,
        )
        if action_plan_exists:
            patches.append(build_remove_section_patch("sec_action_plan"))

        patches.extend(
            [
                build_set_state_patch("action_planning"),
                build_append_section_patch(
                    action_section,
                    before_section_id="sec_main_review",
                ),
                build_set_allowed_events_patch(RISK_AND_ACTION_ALLOWED_EVENTS),
                build_set_risk_summary_patch(
                    build_risk_summary(
                        "high",
                        "已确认存在风险，请继续补充说明并制定行动计划。",
                        [
                            "风险结论已切换为有风险。",
                            "行动计划候选项已生成。",
                            f"风险认定说明：{current_reason or '未填写'}",
                        ],
                    )
                ),
                build_prepend_message_patch(
                    build_message(
                        message_id=f"msg_enter_action_plan_{runtime_event.id}",
                        role="agent",
                        title="已展开行动计划",
                        body="系统已根据“有风险”结论展开行动计划区域，请勾选或补充行动事项后确认。",
                        tone="warning",
                        timestamp=runtime_event.timestamp,
                    )
                ),
            ]
        )
    else:
        if action_plan_exists:
            patches.append(build_remove_section_patch("sec_action_plan"))
        patches.extend(
            [
                build_set_state_patch("risk_identifying"),
                build_set_allowed_events_patch(RISK_IDENTIFICATION_ALLOWED_EVENTS),
            ]
        )

    return patches


def build_update_risk_reason_patches(
    *,
    envelope: Dict[str, Any],
    event: Dict[str, Any],
) -> List[Dict[str, Any]]:
    runtime_event = RuntimeEvent.from_dict(event)
    current_decision, _ = _find_risk_identification_state(envelope)
    reason = str((runtime_event.payload or {}).get("label", "")).strip()
    logger.info(
        "Processing update_risk_reason: event_id=%s reason_length=%s",
        runtime_event.id,
        len(reason),
    )
    if not reason:
        return [
            build_prepend_message_patch(
                build_message(
                    message_id=f"msg_update_risk_reason_invalid_{runtime_event.id}",
                    role="system",
                    title="风险认定说明保存失败",
                    body="请输入有效的风险认定说明后再保存。",
                    tone="warning",
                    timestamp=runtime_event.timestamp,
                )
            )
        ]

    section = build_risk_identification_section(
        decision=current_decision,
        reason=reason,
    )
    return [
        build_replace_section_patch("sec_risk_identification", section),
        build_prepend_message_patch(
            build_message(
                message_id=f"msg_update_risk_reason_{runtime_event.id}",
                role="system",
                title="风险认定说明已保存",
                body="当前风险认定说明已回写到风险认定区。",
                tone="success",
                timestamp=runtime_event.timestamp,
            )
        ),
    ]


def build_resolve_no_risk_patches(
    *,
    envelope: Dict[str, Any],
    event: Dict[str, Any],
) -> List[Dict[str, Any]]:
    runtime_event = RuntimeEvent.from_dict(event)
    current_decision, current_reason = _find_risk_identification_state(envelope)
    logger.info(
        "Processing resolve_no_risk: event_id=%s decision=%s",
        runtime_event.id,
        current_decision,
    )
    if current_decision != "no_risk":
        return [
            build_prepend_message_patch(
                build_message(
                    message_id=f"msg_resolve_no_risk_invalid_{runtime_event.id}",
                    role="system",
                    title="无法执行解警",
                    body="请先在风险认定中明确选择“无风险”，再执行解警。",
                    tone="warning",
                    timestamp=runtime_event.timestamp,
                )
            )
        ]

    resolution_section = build_no_risk_resolution_section(current_reason)
    patches: List[Dict[str, Any]] = [
        build_set_state_patch("resolved_no_risk"),
        build_remove_section_patch("sec_risk_identification"),
        build_append_section_patch(
            resolution_section,
            before_section_id="sec_main_review",
        ),
        build_set_allowed_events_patch(["open_detail"]),
        build_set_risk_summary_patch(
            build_risk_summary(
                "low",
                "风险认定结果为无风险，当前预警已完成解警处理。",
                [
                    "解警动作已触发。",
                    "当前任务已处理完成。",
                    f"风险认定说明：{current_reason or '未填写'}",
                ],
            )
        ),
        build_prepend_message_patch(
            build_message(
                message_id=f"msg_resolve_no_risk_{runtime_event.id}",
                role="agent",
                title="已完成解警",
                body="系统已根据“无风险”认定结果执行解警，当前预警核查任务已完成。",
                tone="success",
                timestamp=runtime_event.timestamp,
            )
        ),
    ]

    if _find_section(envelope, "sec_report_actions") is not None:
        patches.insert(1, build_remove_section_patch("sec_report_actions"))

    return patches


def build_confirm_risk_identification_patches(
    *,
    envelope: Dict[str, Any],
    event: Dict[str, Any],
) -> List[Dict[str, Any]]:
    runtime_event = RuntimeEvent.from_dict(event)
    current_decision, current_reason = _find_risk_identification_state(envelope)
    logger.info(
        "Processing confirm_risk_identification: event_id=%s decision=%s",
        runtime_event.id,
        current_decision,
    )

    if current_decision != "has_risk":
        return [
            build_prepend_message_patch(
                build_message(
                    message_id=f"msg_confirm_risk_invalid_{runtime_event.id}",
                    role="system",
                    title="无法进入行动计划",
                    body="请先在风险认定中明确选择“有风险”，再进入行动计划阶段。",
                    tone="warning",
                    timestamp=runtime_event.timestamp,
                )
            )
        ]

    action_section = build_action_plan_section(
        items=_build_default_action_plan_items(),
        reason=current_reason,
    )
    patches: List[Dict[str, Any]] = [
        build_set_state_patch("action_planning"),
        build_remove_section_patch("sec_risk_identification"),
        build_append_section_patch(action_section, before_section_id="sec_main_review"),
        build_set_allowed_events_patch(ACTION_PLANNING_ALLOWED_EVENTS),
        build_set_risk_summary_patch(
            build_risk_summary(
                "high",
                "已确认存在风险，请制定并确认后续行动计划。",
                [
                    "风险认定结果为有风险。",
                    "行动计划候选项已生成。",
                    f"风险认定说明：{current_reason or '未填写'}",
                ],
            )
        ),
        build_prepend_message_patch(
            build_message(
                message_id=f"msg_confirm_risk_{runtime_event.id}",
                role="agent",
                title="已进入行动计划阶段",
                body="系统已根据“有风险”认定结果打开行动计划清单，请勾选或补充行动事项后确认。",
                tone="warning",
                timestamp=runtime_event.timestamp,
            )
        ),
    ]

    if _find_section(envelope, "sec_report_actions") is not None:
        patches.insert(2, build_remove_section_patch("sec_report_actions"))

    if _find_section(envelope, "sec_action_plan") is not None:
        patches.insert(2, build_remove_section_patch("sec_action_plan"))

    return patches


def build_toggle_action_item_patches(
    *,
    envelope: Dict[str, Any],
    event: Dict[str, Any],
) -> List[Dict[str, Any]]:
    runtime_event = RuntimeEvent.from_dict(event)
    checklist = _find_action_plan_checklist(envelope)
    if not checklist:
        logger.warning(
            "toggle_action_item skipped: section_or_checklist_missing event_id=%s",
            runtime_event.id,
        )
        return []

    item_id = str((runtime_event.payload or {}).get("itemId", ""))
    logger.info(
        "Processing toggle_action_item: event_id=%s item_id=%s",
        runtime_event.id,
        item_id,
    )

    next_items = [
        {**item, "checked": not item.get("checked", False)} if item["id"] == item_id else item
        for item in checklist["props"]["items"]
    ]
    section = _rebuild_action_plan_section(envelope, next_items)

    selected_count = sum(1 for item in next_items if item.get("checked"))
    return [
        build_replace_section_patch("sec_action_plan", section),
        build_prepend_message_patch(
            build_message(
                message_id=f"msg_toggle_action_{runtime_event.id}",
                role="user",
                title="行动计划已更新",
                body=f"当前已选择 {selected_count} 项行动事项。",
                tone="info",
                timestamp=runtime_event.timestamp,
            )
        ),
    ]


def build_add_action_item_patches(
    *,
    envelope: Dict[str, Any],
    event: Dict[str, Any],
) -> List[Dict[str, Any]]:
    runtime_event = RuntimeEvent.from_dict(event)
    normalized_label = str((runtime_event.payload or {}).get("label", "")).strip()
    checklist = _find_action_plan_checklist(envelope)
    logger.info(
        "Processing add_action_item: event_id=%s label=%s",
        runtime_event.id,
        normalized_label,
    )

    if not checklist or not normalized_label:
        return [
            build_prepend_message_patch(
                build_message(
                    message_id=f"msg_add_action_invalid_{runtime_event.id}",
                    role="system",
                    title="新增行动事项失败",
                    body="请输入有效的行动事项内容后再提交。",
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
                    message_id=f"msg_add_action_duplicate_{runtime_event.id}",
                    role="system",
                    title="行动事项已存在",
                    body=f"“{normalized_label}”已在当前行动计划中，无需重复添加。",
                    tone="warning",
                    timestamp=runtime_event.timestamp,
                )
            )
        ]

    next_item = {
        "id": f"item_action_custom_{runtime_event.id}",
        "label": normalized_label,
        "description": "由核查人员在行动计划阶段手动补充。",
        "checked": True,
    }
    next_items = [next_item, *checklist["props"]["items"]]
    section = _rebuild_action_plan_section(envelope, next_items)

    return [
        build_replace_section_patch("sec_action_plan", section),
        build_prepend_message_patch(
            build_message(
                message_id=f"msg_add_action_{runtime_event.id}",
                role="agent",
                title="行动事项已添加",
                body=f"已将新的行动事项“{normalized_label}”加入行动计划，并默认选中。",
                tone="success",
                timestamp=runtime_event.timestamp,
            )
        ),
    ]


def build_confirm_action_plan_patches(
    *,
    envelope: Dict[str, Any],
    event: Dict[str, Any],
) -> List[Dict[str, Any]]:
    runtime_event = RuntimeEvent.from_dict(event)
    current_decision, current_reason = _find_risk_identification_state(envelope)
    selected_items = _checked_action_items(envelope)
    logger.info(
        "Processing confirm_action_plan: event_id=%s selected_items=%s",
        runtime_event.id,
        len(selected_items),
    )

    if not selected_items:
        return [
            build_prepend_message_patch(
                build_message(
                    message_id=f"msg_confirm_action_invalid_{runtime_event.id}",
                    role="system",
                    title="无法确认行动计划",
                    body="请至少勾选一项推荐行动，或新增一项行动事项后再确认。",
                    tone="warning",
                    timestamp=runtime_event.timestamp,
                )
            )
        ]

    selected_labels = [str(item["label"]) for item in selected_items]
    resolution_section = build_action_resolution_section(
        reason=current_reason,
        actions=selected_labels,
    )

    return [
        build_set_state_patch("resolved_with_action"),
        build_remove_section_patch("sec_action_plan"),
        build_append_section_patch(
            resolution_section,
            before_section_id="sec_main_review",
        ),
        build_set_allowed_events_patch(["open_detail"]),
        build_set_risk_summary_patch(
            build_risk_summary(
                "high",
                "风险认定与行动计划已确认，当前预警核查任务已完成。",
                [
                    "风险认定结果为有风险。",
                    f"已确认 {len(selected_labels)} 项行动计划。",
                    f"风险认定说明：{current_reason or '未填写'}",
                ],
            )
        ),
        build_prepend_message_patch(
            build_message(
                message_id=f"msg_confirm_action_{runtime_event.id}",
                role="agent",
                title="行动计划已确认",
                body="系统已保存本次行动计划，当前预警核查任务已处理完成。",
                tone="success",
                timestamp=runtime_event.timestamp,
            )
        ),
    ]


def build_open_detail_patches(
    *,
    event: Dict[str, Any],
) -> List[Dict[str, Any]]:
    runtime_event = RuntimeEvent.from_dict(event)
    payload = runtime_event.payload or {}
    case_id = str(payload.get("caseId", "-"))
    applicant = str(payload.get("applicant", "-"))
    amount = str(payload.get("amount", "-"))
    logger.info(
        "Processing open_detail: event_id=%s case_id=%s applicant=%s amount=%s",
        runtime_event.id,
        case_id,
        applicant,
        amount,
    )

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
