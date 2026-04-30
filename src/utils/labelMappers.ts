import type { RiskLevel, WorkflowState } from "../types/workflow";

export function mapWorkflowStateLabel(state: WorkflowState): string {
  switch (state) {
    case "reviewing":
      return "核查中";
    case "report_reviewing":
      return "核查报告待处理";
    case "risk_identifying":
      return "风险认定中";
    case "action_planning":
      return "行动计划中";
    case "resolved_no_risk":
      return "已解警";
    case "resolved_with_action":
      return "已确认行动计划";
    case "presenting_result":
      return "展示结果";
    case "awaiting_revision":
      return "等待修改";
    default:
      return state;
  }
}

export function mapWorkflowStateTagType(
  state: WorkflowState,
): "primary" | "success" | "warning" | "danger" {
  switch (state) {
    case "resolved_no_risk":
      return "success";
    case "resolved_with_action":
      return "danger";
    case "report_reviewing":
    case "risk_identifying":
    case "action_planning":
    case "awaiting_revision":
      return "warning";
    case "presenting_result":
      return "success";
    case "reviewing":
    default:
      return "primary";
  }
}

export function mapRiskLevelLabel(level: RiskLevel): string {
  switch (level) {
    case "low":
      return "低风险";
    case "medium":
      return "中风险";
    case "high":
      return "高风险";
    default:
      return level;
  }
}

export function mapRiskLevelTagType(
  level: RiskLevel,
): "success" | "warning" | "danger" {
  switch (level) {
    case "high":
      return "danger";
    case "medium":
      return "warning";
    case "low":
    default:
      return "success";
  }
}
