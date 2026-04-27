import type { PatchPlannerModel } from "./PatchPlannerAgent";
import type { PatchPlanningInput, PatchPlanningOutput } from "./contracts";
import type {
  ChecklistComponent,
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
          description: "由审核人在当前工作流中手动补充。",
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

function buildResultSection(sectionId: string, decision: string): UISection {
  const approved = decision === "approve";

  return {
    id: sectionId,
    title: approved ? "审核结果" : "退回结果",
    description: "这一节内容由模拟智能体作为 Patch 结果返回。",
    components: [
      {
        id: "cmp_result",
        type: "result_summary",
        props: {
          status: approved ? "success" : "warning",
          headline: approved ? "已批准" : "已退回修改",
          summary: approved
            ? "审核人已批准该案件，智能体可以继续执行后续流程。"
            : "审核人要求补充修改，智能体需要在继续前重新生成方案。",
          nextSteps: approved
            ? [
                "通知下游自动化服务继续处理。",
                "将审核确认写入审计记录。",
              ]
            : [
                "将案件连同审核意见退回给智能体。",
                "待补齐政策材料后重新生成提交包。",
              ],
        },
      },
    ],
  };
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
        title: "清单已更新",
        body: `审核人已将清单进度更新为 ${checkedCount} 项已完成。`,
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
          title: "新增审核事项失败",
          body: "请输入有效的审核事项内容后再提交。",
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
          title: "审核事项已存在",
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
        title: "审核事项已添加",
        body: `已将新的审核事项“${nextState.normalizedLabel}”加入当前清单。`,
        tone: "success",
        timestamp: event.timestamp,
      },
    },
    {
      op: "set_risk_summary",
      value: {
        ...envelope.riskSummary,
        details: [
          `人工补充审核事项：${nextState.normalizedLabel}`,
          ...envelope.riskSummary.details,
        ].slice(0, 5),
      },
    },
  ];
}

function handleSubmitDecision(
  _envelope: WorkflowEnvelope,
  event: WorkflowEvent,
): PatchOperation[] {
  const decision = String(event.payload?.decision ?? "revise");
  const sectionId = "sec_main_review";

  return [
    {
      op: "set_state",
      value: decision === "approve" ? "presenting_result" : "awaiting_revision",
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
        level: decision === "approve" ? "low" : "medium",
        summary:
          decision === "approve"
            ? "审核人已批准案件，运行时已准备进入最终执行阶段。"
            : "审核人要求先补充修改，案件暂不能继续流转。",
        details:
          decision === "approve"
            ? ["人工审核已顺利完成。"]
            : ["智能体需要调整方案并重新提交。"],
      },
    },
    {
      op: "prepend_message",
      value: {
        id: `msg_decision_${event.id}`,
        role: "agent",
        title: "Patch 已应用",
        body:
          decision === "approve"
            ? "运行时已接收批准类 Patch，并完成界面更新。"
            : "运行时已接收退回修改类 Patch，并完成界面切换。",
        tone: decision === "approve" ? "success" : "warning",
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
  toggle_check: handleToggleCheck,
  add_checklist_item: handleAddChecklistItem,
  submit_decision: handleSubmitDecision,
  open_detail: handleOpenDetail,
};

/**
 * 当前项目内置的模拟 Patch Planner。
 * 作用是先把 Agent 的输入输出协议跑通，后续再替换成真实模型。
 */
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
