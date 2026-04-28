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

function findReviewChecklist(envelope: WorkflowEnvelope): {
  section: UISection;
  checklist: ChecklistComponent;
} | null {
  const section = envelope.page.sections.find(
    (entry) => entry.id === "sec_main_review",
  );
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
  const section = envelope.page.sections.find((entry) => entry.id === "sec_overview");
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

function buildResultSection(sectionId: string, decision: string): UISection {
  const approved = decision === "approve";

  return {
    id: sectionId,
    title: approved ? "核查结果" : "退回结果",
    description: "这一节内容由模拟智能体作为 Patch 结果返回。",
    components: [
      {
        id: "cmp_result",
        type: "result_summary",
        props: {
          status: approved ? "success" : "warning",
          headline: approved ? "已完成核查" : "已退回补充",
          summary: approved
            ? "核查人员已完成预警核查，相关信息可进入后续处置流程。"
            : "核查人员要求补充更多材料后再继续处理该预警。",
          nextSteps: approved
            ? [
                "将核查结论同步给后续处置系统。",
                "保留当前核查记录作为审计依据。",
              ]
            : [
                "通知相关团队补充证明材料。",
                "待材料齐全后重新发起核查流程。",
              ],
        },
      },
    ],
  };
}

function buildReviewReportText(envelope: WorkflowEnvelope): string {
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
      : "- 暂无已勾选的核查事项";

  const pendingContent =
    uncheckedItems.length > 0
      ? uncheckedItems.map((item) => `- ${item.label}`).join("\n")
      : "- 无待补充事项";

  return [
    "核查报告",
    "",
    "预警基本情况",
    ...(profileLines.length > 0 ? profileLines : ["- 暂无预警详情信息"]),
    "",
    "已核查内容",
    reviewedContent,
    "",
    "待补充关注项",
    pendingContent,
    "",
    "核查结论",
    "核查人员已完成本次预警核查。结合当前预警详情、核查清单执行情况与审批列表信息，建议将该预警移交后续处置流程，并保留当前记录作为审计依据。",
  ].join("\n");
}

function buildReviewReportSection(envelope: WorkflowEnvelope): UISection {
  return {
    id: "sec_review_report",
    title: "核查报告",
    description: "由运行时在完成核查后生成的结构化报告。",
    components: [
      {
        id: "cmp_review_report",
        type: "text",
        props: {
          content: buildReviewReportText(envelope),
          variant: "body",
        },
      },
    ],
  };
}

function buildReviewReportPatches(envelope: WorkflowEnvelope): PatchOperation[] {
  const reportSection = buildReviewReportSection(envelope);
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
      op: "set_allowed_events",
      value: envelope.allowedEvents.filter((eventType) => eventType !== "init_event"),
    },
    {
      op: "set_risk_summary",
      value: {
        level: "high",
        summary: "预警详情已初始化完成，当前预警需尽快进入人工核查。",
        details: [
          "命中高频异常交易预警。",
          "客户已被标记为待人工核查。",
          "初始化数据由服务端 patch 回填完成。",
        ],
      },
    },
    {
      op: "prepend_message",
      value: {
        id: `msg_init_${event.id}`,
        role: "system",
        title: "预警详情已初始化",
        body: "服务端已返回 init_event 对应的 patch，并更新了“预警情况详情”区块。",
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
        title: "核查清单已更新",
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
          title: "新增核查事项失败",
          body: "请输入有效的核查事项内容后再提交。",
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
          title: "核查事项已存在",
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
        title: "核查事项已添加",
        body: `已将新的核查事项“${nextState.normalizedLabel}”加入当前清单。`,
        tone: "success",
        timestamp: event.timestamp,
      },
    },
    {
      op: "set_risk_summary",
      value: {
        ...envelope.riskSummary,
        details: [
          `人工补充核查事项：${nextState.normalizedLabel}`,
          ...envelope.riskSummary.details,
        ].slice(0, 5),
      },
    },
  ];
}

function handleSubmitDecision(
  envelope: WorkflowEnvelope,
  event: WorkflowEvent,
): PatchOperation[] {
  const decision = String(event.payload?.decision ?? "revise");

  if (decision === "approve") {
    return [
      {
        op: "set_state",
        value: "presenting_result",
      },
      ...buildReviewReportPatches(envelope),
      {
        op: "set_allowed_events",
        value: [],
      },
      {
        op: "set_risk_summary",
        value: {
          level: "low",
          summary: "核查人员已完成预警核查，运行时已准备进入最终处置阶段。",
          details: [
            "人工核查已顺利完成。",
            "核查报告已生成，可作为后续处置与审计依据。",
          ],
        },
      },
      {
        op: "prepend_message",
        value: {
          id: `msg_decision_${event.id}`,
          role: "agent",
          title: "核查报告已生成",
          body: "运行时已接收批准事件，并在页面中追加核查报告 section。",
          tone: "success",
          timestamp: event.timestamp,
        },
      },
    ];
  }

  const sectionId = "sec_main_review";

  return [
    {
      op: "set_state",
      value: "awaiting_revision",
    },
    {
      op: "replace_section",
      sectionId,
      value: buildResultSection(sectionId, decision),
    },
    {
      op: "set_allowed_events",
      value: [],
    },
    {
      op: "set_risk_summary",
      value: {
        level: "medium",
        summary: "核查人员要求先补充修改，当前预警暂不能继续流转。",
        details: ["需要补充更多核查材料后再重新提交。"],
      },
    },
    {
      op: "prepend_message",
      value: {
        id: `msg_decision_${event.id}`,
        role: "agent",
        title: "Patch 已应用",
        body: "运行时已接收退回修改类 Patch，并完成界面切换。",
        tone: "warning",
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
        body: `已请求查看案件 ${caseId} 的详情。申请方：${applicant}，申请金额：${amount}。后续可在这里接入真实详情抽屉或侧边面板。`,
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
  submit_decision: handleSubmitDecision,
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
