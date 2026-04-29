/**
 * 当前项目的 mock Patch Planner。
 * 作用是模拟 Agent 根据事件和上下文生成 PatchOperation[]，帮助验证完整运行链路。
 * 后续接真实模型时，优先替换这里的生成逻辑，而不是改 renderer 或 widget。
 */
import type { PatchPlannerModel } from "./PatchPlannerAgent";
import type { PatchPlanningInput, PatchPlanningOutput } from "./contracts";
import type {
  ChecklistComponent,
  KeyValueComponent,
  PatchOperation,
  UISection,
  WorkflowEnvelope,
  WorkflowEvent,
} from "../types/workflow";

type PatchHandler = (
  envelope: WorkflowEnvelope,
  event: WorkflowEvent,
) => PatchOperation[];

function findSection(
  envelope: WorkflowEnvelope,
  sectionId: string,
): UISection | null {
  return envelope.page.sections.find((entry) => entry.id === sectionId) ?? null;
}

function findReviewChecklist(envelope: WorkflowEnvelope): {
  section: UISection;
  checklist: ChecklistComponent;
} | null {
  const section = findSection(envelope, "sec_main_review");
  const checklist = section?.components.find(
    (component): component is ChecklistComponent => component.type === "checklist",
  );

  if (!section || !checklist) {
    return null;
  }

  return { section, checklist };
}

function findOverviewKeyValue(
  envelope: WorkflowEnvelope,
): KeyValueComponent | null {
  const section = findSection(envelope, "sec_overview");
  const keyValue = section?.components.find(
    (component): component is KeyValueComponent => component.type === "key_value",
  );

  return keyValue ?? null;
}

function replaceChecklistInSection(
  section: UISection,
  checklist: ChecklistComponent,
): UISection {
  return {
    ...section,
    components: section.components.map((component) =>
      component.id === checklist.id ? checklist : component,
    ),
  };
}

function buildChecklistSection(
  envelope: WorkflowEnvelope,
  event: WorkflowEvent,
): UISection | null {
  const reviewState = findReviewChecklist(envelope);

  if (!reviewState) {
    return null;
  }

  const itemId = String(event.payload?.itemId ?? "");
  const items = reviewState.checklist.props.items.map((item) =>
    item.id === itemId ? { ...item, checked: !item.checked } : item,
  );

  return replaceChecklistInSection(reviewState.section, {
    ...reviewState.checklist,
    props: {
      ...reviewState.checklist.props,
      items,
    },
  });
}

function buildChecklistAdditionSection(
  envelope: WorkflowEnvelope,
  event: WorkflowEvent,
): { section: UISection; normalizedLabel: string } | null {
  const reviewState = findReviewChecklist(envelope);

  if (!reviewState) {
    return null;
  }

  const normalizedLabel = String(event.payload?.label ?? "").trim();

  if (!normalizedLabel) {
    return null;
  }

  const exists = reviewState.checklist.props.items.some(
    (item) => item.label.trim().toLowerCase() === normalizedLabel.toLowerCase(),
  );

  if (exists) {
    return {
      section: reviewState.section,
      normalizedLabel,
    };
  }

  const nextChecklist: ChecklistComponent = {
    ...reviewState.checklist,
    props: {
      ...reviewState.checklist.props,
      items: [
        ...reviewState.checklist.props.items,
        {
          id: `item_custom_${event.id}`,
          label: normalizedLabel,
          description: "由核查人员在当前工作流中手动补充。",
          checked: false,
        },
      ],
    },
  };

  return {
    section: replaceChecklistInSection(reviewState.section, nextChecklist),
    normalizedLabel,
  };
}

function buildWarningDetailSection(): UISection {
  return {
    id: "sec_overview",
    title: "预警情况详情",
    description: "该区域内容由初始化事件触发后，通过服务端 patch 回填。",
    components: [
      {
        id: "cmp_warning_detail",
        type: "key_value",
        props: {
          layout: "grid",
          columns: 3,
          minColumnWidth: 220,
          items: [
            { label: "预警编号", value: "WARN-20260428-017" },
            { label: "客户名称", value: "华东星联贸易有限公司" },
            { label: "预警类型", value: "高频异常交易预警" },
            { label: "命中时间", value: "2026-04-28 09:03" },
            { label: "风险等级", value: "高风险" },
            { label: "当前状态", value: "待人工核查" },
          ],
        },
      },
    ],
  };
}

function buildReviewDirectionSection(): UISection {
  return {
    id: "sec_main_review",
    title: "核查方向",
    description: "由服务端返回的核查建议与人工补充方向组成。",
    components: [
      {
        id: "cmp_checklist",
        type: "checklist",
        props: {
          action: {
            eventType: "toggle_check",
          },
          items: [
            {
              id: "item_account_flow",
              label: "核查近 7 日异常交易流水的真实业务背景",
              description: "确认短时间内高频转入转出是否有真实贸易或结算依据。",
              checked: false,
            },
            {
              id: "item_counterparty",
              label: "核验交易对手与受益人之间是否存在隐性关联",
              description: "关注法人、联系电话、开户地址及历史交易网络中的重叠关系。",
              checked: false,
            },
            {
              id: "item_region",
              label: "核查资金是否流向高风险地区或敏感通道",
              description: "重点关注是否存在绕道结算、拆单转移或异常跨境路径。",
              checked: false,
            },
            {
              id: "item_documents",
              label: "补充核验业务合同、发票与物流凭证的一致性",
              description: "确认基础贸易资料是否与本次预警触发交易相匹配。",
              checked: false,
            },
          ],
        },
      },
      {
        id: "cmp_custom_check_input",
        type: "text_input",
        props: {
          eventType: "add_checklist_item",
          label: "新增核查方向",
          placeholder: "例如：核验交易对手与受益人是否存在隐性关联",
          buttonLabel: "添加到清单",
          helperText: "输入后会由运行时生成 patch，并把新的核查方向回写到当前 checklist。",
          clearOnSubmit: true,
        },
      },
      {
        id: "cmp_actions",
        type: "button_group",
        props: {
          actions: [
            {
              label: "执行核查",
              eventType: "Risk_Check_Event",
              payload: { action: "execute" },
              buttonType: "primary",
            },
            {
              label: "Save核查",
              eventType: "Risk_Check_Event",
              payload: { action: "execute" },
              buttonType: "second",
            },
          ],
        },
      },
    ],
  };
}

function buildRiskCheckReportText(envelope: WorkflowEnvelope): string {
  const keyValue = findOverviewKeyValue(envelope);
  const reviewState = findReviewChecklist(envelope);

  const profileLines = (keyValue?.props.items ?? []).map(
    (item) => `- ${item.label}：${item.value}`,
  );

  const checkedItems =
    reviewState?.checklist.props.items.filter((item) => item.checked) ?? [];
  const uncheckedItems =
    reviewState?.checklist.props.items.filter((item) => !item.checked) ?? [];

  const reviewedContent =
    checkedItems.length > 0
      ? checkedItems.map((item) => `- ${item.label}`).join("\n")
      : "- 当前尚未勾选已完成的核查方向";

  const pendingContent =
    uncheckedItems.length > 0
      ? uncheckedItems.map((item) => `- ${item.label}`).join("\n")
      : "- 无待执行核查方向";

  return [
    "风险核查报告",
    "",
    "预警基本情况",
    ...(profileLines.length > 0 ? profileLines : ["- 暂无预警详情信息"]),
    "",
    "已执行核查内容",
    reviewedContent,
    "",
    "待继续关注方向",
    pendingContent,
    "",
    "核查结论",
    "系统已根据当前预警详情与核查方向执行风险核查。综合现有信息判断，该客户交易行为存在较高可疑度，建议继续升级人工处置，并保留本次核查过程作为后续审计依据。",
  ].join("\n");
}

function buildRiskCheckReportSection(envelope: WorkflowEnvelope): UISection {
  return {
    id: "sec_review_report",
    title: "核查报告",
    description: "由 Risk_Check_Event 触发后返回的核查报告。",
    components: [
      {
        id: "cmp_review_report",
        type: "text",
        props: {
          content: buildRiskCheckReportText(envelope),
          variant: "body",
        },
      },
    ],
  };
}

function buildRiskCheckReportPatches(envelope: WorkflowEnvelope): PatchOperation[] {
  const reportSection = buildRiskCheckReportSection(envelope);
  const exists = envelope.page.sections.some(
    (section) => section.id === reportSection.id,
  );

  if (exists) {
    return [
      {
        op: "remove_section",
        sectionId: reportSection.id,
      },
      {
        op: "append_section",
        value: reportSection,
        beforeSectionId: "sec_main_review",
      },
    ];
  }

  return [
    {
      op: "append_section",
      value: reportSection,
      beforeSectionId: "sec_main_review",
    },
  ];
}

function handleInitEvent(
  envelope: WorkflowEnvelope,
  event: WorkflowEvent,
): PatchOperation[] {
  return [
    {
      op: "replace_section",
      sectionId: "sec_overview",
      value: buildWarningDetailSection(),
    },
    {
      op: "replace_section",
      sectionId: "sec_main_review",
      value: buildReviewDirectionSection(),
    },
    {
      op: "set_allowed_events",
      value: [
        "toggle_check",
        "add_checklist_item",
        "Risk_Check_Event",
        "open_detail",
      ],
    },
    {
      op: "set_risk_summary",
      value: {
        level: "high",
        summary: "预警详情与核查方向已初始化完成，当前预警需尽快进入人工核查。",
        details: [
          "命中高频异常交易预警。",
          "系统已回填 4 条核查建议。",
          "当前状态为待人工核查。",
        ],
      },
    },
    {
      op: "prepend_message",
      value: {
        id: `msg_init_${event.id}`,
        role: "system",
        title: "预警详情已初始化",
        body: "服务端已返回 init_event 对应的 patch，并更新了“预警情况详情”与“核查方向”区块。",
        tone: "success",
        timestamp: event.timestamp,
      },
    },
  ];
}

function handleToggleCheck(
  envelope: WorkflowEnvelope,
  event: WorkflowEvent,
): PatchOperation[] {
  const nextSection = buildChecklistSection(envelope, event);

  if (!nextSection) {
    return [];
  }

  const checkedCount = nextSection.components
    .flatMap((component) =>
      component.type === "checklist" ? component.props.items : [],
    )
    .filter((item) => item.checked).length;

  return [
    {
      op: "replace_section",
      sectionId: nextSection.id,
      value: nextSection,
    },
    {
      op: "prepend_message",
      value: {
        id: `msg_toggle_${event.id}`,
        role: "user",
        title: "核查方向已更新",
        body: `核查人员已将清单进度更新为 ${checkedCount} 项已完成。`,
        tone: "info",
        timestamp: event.timestamp,
      },
    },
  ];
}

function handleAddChecklistItem(
  envelope: WorkflowEnvelope,
  event: WorkflowEvent,
): PatchOperation[] {
  const reviewState = findReviewChecklist(envelope);
  const normalizedLabel = String(event.payload?.label ?? "").trim();

  if (!reviewState || !normalizedLabel) {
    return [
      {
        op: "prepend_message",
        value: {
          id: `msg_add_check_invalid_${event.id}`,
          role: "system",
          title: "新增核查方向失败",
          body: "请输入有效的核查方向内容后再提交。",
          tone: "warning",
          timestamp: event.timestamp,
        },
      },
    ];
  }

  const exists = reviewState.checklist.props.items.some(
    (item) => item.label.trim().toLowerCase() === normalizedLabel.toLowerCase(),
  );

  if (exists) {
    return [
      {
        op: "prepend_message",
        value: {
          id: `msg_add_check_duplicate_${event.id}`,
          role: "system",
          title: "核查方向已存在",
          body: `“${normalizedLabel}” 已在当前清单中，无需重复添加。`,
          tone: "warning",
          timestamp: event.timestamp,
        },
      },
    ];
  }

  const nextState = buildChecklistAdditionSection(envelope, event);

  if (!nextState) {
    return [];
  }

  return [
    {
      op: "replace_section",
      sectionId: nextState.section.id,
      value: nextState.section,
    },
    {
      op: "prepend_message",
      value: {
        id: `msg_add_check_${event.id}`,
        role: "agent",
        title: "核查方向已添加",
        body: `已将新的核查方向“${nextState.normalizedLabel}”加入当前清单。`,
        tone: "success",
        timestamp: event.timestamp,
      },
    },
    {
      op: "set_risk_summary",
      value: {
        ...envelope.riskSummary,
        details: [
          `人工补充核查方向：${nextState.normalizedLabel}`,
          ...envelope.riskSummary.details,
        ].slice(0, 5),
      },
    },
  ];
}

function handleRiskCheckEvent(
  envelope: WorkflowEnvelope,
  event: WorkflowEvent,
): PatchOperation[] {
  return [
    {
      op: "set_state",
      value: "presenting_result",
    },
    ...buildRiskCheckReportPatches(envelope),
    {
      op: "set_allowed_events",
      value: [],
    },
    {
      op: "set_risk_summary",
      value: {
        level: "high",
        summary: "风险核查已执行完成，建议将当前预警升级进入后续处置流程。",
        details: [
          "核查报告已生成。",
          "命中预警的关键方向已进入人工复核结论。",
          "建议保留全部核查轨迹作为审计依据。",
        ],
      },
    },
    {
      op: "prepend_message",
      value: {
        id: `msg_risk_check_${event.id}`,
        role: "agent",
        title: "核查报告已生成",
        body: "运行时已接收 Risk_Check_Event，并将核查结果写入报告区块。",
        tone: "success",
        timestamp: event.timestamp,
      },
    },
  ];
}

function handleOpenDetail(
  _envelope: WorkflowEnvelope,
  event: WorkflowEvent,
): PatchOperation[] {
  const caseId = String(event.payload?.caseId ?? "-");
  const applicant = String(event.payload?.applicant ?? "-");
  const amount = String(event.payload?.amount ?? "-");

  return [
    {
      op: "prepend_message",
      value: {
        id: `msg_detail_${event.id}`,
        role: "agent",
        title: "详情已展开",
        body: `已请求查看案件 ${caseId} 的详情。客户名称：${applicant}，关联金额：${amount}。后续可在这里接入真实详情抽屉或侧边面板。`,
        tone: "info",
        timestamp: event.timestamp,
      },
    },
  ];
}

const handlers: Record<string, PatchHandler> = {
  init_event: handleInitEvent,
  toggle_check: handleToggleCheck,
  add_checklist_item: handleAddChecklistItem,
  Risk_Check_Event: handleRiskCheckEvent,
  open_detail: handleOpenDetail,
};

export class MockPatchPlannerModel implements PatchPlannerModel {
  async generate(input: PatchPlanningInput): Promise<PatchPlanningOutput> {
    await new Promise((resolve) => window.setTimeout(resolve, 180));
    const patches = handlers[input.event.type]?.(input.envelope, input.event) ?? [];

    return {
      patches,
      rationale: `模拟 Patch Planner 已根据事件“${input.event.type}”生成 ${patches.length} 个补丁操作，用于表达这次工作流状态迁移。`,
      warnings: [],
    };
  }
}
