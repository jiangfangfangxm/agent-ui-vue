import type { RiskLevel, WorkflowState } from "../types/workflow";

export function mapWorkflowStateLabel(state: WorkflowState): string {
  switch (state) {
    case "reviewing":
      return "审核中";
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
): "primary" | "success" | "warning" {
  switch (state) {
    case "presenting_result":
      return "success";
    case "awaiting_revision":
      return "warning";
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
