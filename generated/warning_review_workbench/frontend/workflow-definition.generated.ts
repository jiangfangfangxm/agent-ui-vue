/* AUTO-GENERATED from app DSL. Do not edit by hand. */
import type { WorkflowEventInput, WorkflowState } from "../../src/types/workflow";

export type GeneratedWorkflowEventType =
  | "init_event"
  | "toggle_check"
  | "add_checklist_item"
  | "Risk_Check_Event"
  | "edit_report"
  | "save_report_revision"
  | "cancel_report_revision"
  | "add_review_direction_after_report"
  | "submit_new_direction_after_report"
  | "cancel_add_direction"
  | "enter_risk_identification"
  | "set_risk_decision"
  | "update_risk_reason"
  | "resolve_no_risk"
  | "confirm_risk_identification"
  | "toggle_action_item"
  | "add_action_item"
  | "confirm_action_plan"
  | "open_detail";

type PayloadValidator = (payload: Record<string, unknown>) => boolean;

interface GeneratedEventContract {
  eventType: GeneratedWorkflowEventType;
  allowedStates: WorkflowState[];
  validatePayload: PayloadValidator;
}

function hasNonEmptyString(payload: Record<string, unknown>, key: string): boolean {
  return typeof payload[key] === "string" && payload[key].trim().length > 0;
}

const optionalPayload: PayloadValidator = () => true;

export const generatedEventContracts: Record<GeneratedWorkflowEventType, GeneratedEventContract> = {
  "init_event": {
    eventType: "init_event",
    allowedStates: ["reviewing"] as WorkflowState[],
    validatePayload: optionalPayload,
  },
  "toggle_check": {
    eventType: "toggle_check",
    allowedStates: ["reviewing", "report_reviewing"] as WorkflowState[],
    validatePayload: (payload) => hasNonEmptyString(payload, "itemId"),
  },
  "add_checklist_item": {
    eventType: "add_checklist_item",
    allowedStates: ["reviewing"] as WorkflowState[],
    validatePayload: (payload) => hasNonEmptyString(payload, "label"),
  },
  "Risk_Check_Event": {
    eventType: "Risk_Check_Event",
    allowedStates: ["reviewing"] as WorkflowState[],
    validatePayload: optionalPayload,
  },
  "edit_report": {
    eventType: "edit_report",
    allowedStates: ["report_reviewing"] as WorkflowState[],
    validatePayload: optionalPayload,
  },
  "save_report_revision": {
    eventType: "save_report_revision",
    allowedStates: ["awaiting_revision"] as WorkflowState[],
    validatePayload: (payload) => hasNonEmptyString(payload, "label"),
  },
  "cancel_report_revision": {
    eventType: "cancel_report_revision",
    allowedStates: ["awaiting_revision"] as WorkflowState[],
    validatePayload: optionalPayload,
  },
  "add_review_direction_after_report": {
    eventType: "add_review_direction_after_report",
    allowedStates: ["report_reviewing"] as WorkflowState[],
    validatePayload: optionalPayload,
  },
  "submit_new_direction_after_report": {
    eventType: "submit_new_direction_after_report",
    allowedStates: ["report_reviewing"] as WorkflowState[],
    validatePayload: (payload) => hasNonEmptyString(payload, "label"),
  },
  "cancel_add_direction": {
    eventType: "cancel_add_direction",
    allowedStates: ["report_reviewing"] as WorkflowState[],
    validatePayload: optionalPayload,
  },
  "enter_risk_identification": {
    eventType: "enter_risk_identification",
    allowedStates: ["report_reviewing"] as WorkflowState[],
    validatePayload: optionalPayload,
  },
  "set_risk_decision": {
    eventType: "set_risk_decision",
    allowedStates: ["risk_identifying", "action_planning"] as WorkflowState[],
    validatePayload: (payload) => hasNonEmptyString(payload, "decision") && (["has_risk", "no_risk"] as unknown[]).includes(payload["decision"]),
  },
  "update_risk_reason": {
    eventType: "update_risk_reason",
    allowedStates: ["risk_identifying", "action_planning"] as WorkflowState[],
    validatePayload: (payload) => hasNonEmptyString(payload, "label"),
  },
  "resolve_no_risk": {
    eventType: "resolve_no_risk",
    allowedStates: ["risk_identifying", "action_planning"] as WorkflowState[],
    validatePayload: optionalPayload,
  },
  "confirm_risk_identification": {
    eventType: "confirm_risk_identification",
    allowedStates: ["risk_identifying"] as WorkflowState[],
    validatePayload: optionalPayload,
  },
  "toggle_action_item": {
    eventType: "toggle_action_item",
    allowedStates: ["action_planning"] as WorkflowState[],
    validatePayload: (payload) => hasNonEmptyString(payload, "itemId"),
  },
  "add_action_item": {
    eventType: "add_action_item",
    allowedStates: ["action_planning"] as WorkflowState[],
    validatePayload: (payload) => hasNonEmptyString(payload, "label"),
  },
  "confirm_action_plan": {
    eventType: "confirm_action_plan",
    allowedStates: ["action_planning"] as WorkflowState[],
    validatePayload: optionalPayload,
  },
  "open_detail": {
    eventType: "open_detail",
    allowedStates: ["reviewing", "report_reviewing", "awaiting_revision", "risk_identifying", "action_planning", "resolved_no_risk", "resolved_with_action", "presenting_result"] as WorkflowState[],
    validatePayload: optionalPayload,
  },
};

export const generatedAllowedEventsByState: Record<string, GeneratedWorkflowEventType[]> = {
  "reviewing": ["toggle_check", "add_checklist_item", "Risk_Check_Event", "open_detail"] as GeneratedWorkflowEventType[],
  "report_reviewing": ["edit_report", "add_review_direction_after_report", "enter_risk_identification", "open_detail"] as GeneratedWorkflowEventType[],
  "awaiting_revision": ["save_report_revision", "cancel_report_revision", "open_detail"] as GeneratedWorkflowEventType[],
  "risk_identifying": ["set_risk_decision", "update_risk_reason", "resolve_no_risk", "confirm_risk_identification", "open_detail"] as GeneratedWorkflowEventType[],
  "action_planning": ["set_risk_decision", "update_risk_reason", "resolve_no_risk", "toggle_action_item", "add_action_item", "confirm_action_plan", "open_detail"] as GeneratedWorkflowEventType[],
  "resolved_no_risk": ["open_detail"] as GeneratedWorkflowEventType[],
  "resolved_with_action": ["open_detail"] as GeneratedWorkflowEventType[],
};

export function validateGeneratedEventInput(
  state: WorkflowState,
  input: WorkflowEventInput,
): string | null {
  const contract = generatedEventContracts[input.type as GeneratedWorkflowEventType];
  if (!contract) return `未知事件：${input.type}`;
  if (!contract.allowedStates.includes(state)) return `事件“${input.type}”不属于当前阶段“${state}”`;
  if (!contract.validatePayload(input.payload ?? {})) return `事件“${input.type}”的 payload 不符合契约`;
  return null;
}
