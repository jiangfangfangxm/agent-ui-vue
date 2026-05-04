import type { WorkflowEventInput, WorkflowState } from "../types/workflow";
import { getEventConfig, validatePayloadBySchema } from "./appConfig";

export type WorkflowEventType =
  | "init_event"
  | "toggle_check"
  | "add_checklist_item"
  | "Risk_Check_Event"
  | "open_detail"
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
  | "confirm_action_plan";

type PayloadValidator = (payload: Record<string, unknown>) => boolean;

interface WorkflowEventContract {
  eventType: WorkflowEventType;
  allowedStates: WorkflowState[];
  validatePayload?: PayloadValidator;
}

function hasNonEmptyString(
  payload: Record<string, unknown>,
  key: string,
): boolean {
  return typeof payload[key] === "string" && payload[key].trim().length > 0;
}

const hasOptionalPayload = () => true;

export const workflowEventContracts: Record<
  WorkflowEventType,
  WorkflowEventContract
> = {
  init_event: {
    eventType: "init_event",
    allowedStates: ["reviewing"],
    validatePayload: hasOptionalPayload,
  },
  toggle_check: {
    eventType: "toggle_check",
    allowedStates: ["reviewing", "report_reviewing"],
    validatePayload: (payload) => hasNonEmptyString(payload, "itemId"),
  },
  add_checklist_item: {
    eventType: "add_checklist_item",
    allowedStates: ["reviewing"],
    validatePayload: (payload) => hasNonEmptyString(payload, "label"),
  },
  Risk_Check_Event: {
    eventType: "Risk_Check_Event",
    allowedStates: ["reviewing"],
    validatePayload: hasOptionalPayload,
  },
  open_detail: {
    eventType: "open_detail",
    allowedStates: [
      "reviewing",
      "report_reviewing",
      "risk_identifying",
      "action_planning",
      "resolved_no_risk",
      "resolved_with_action",
      "presenting_result",
      "awaiting_revision",
    ],
    validatePayload: hasOptionalPayload,
  },
  edit_report: {
    eventType: "edit_report",
    allowedStates: ["report_reviewing"],
    validatePayload: hasOptionalPayload,
  },
  save_report_revision: {
    eventType: "save_report_revision",
    allowedStates: ["awaiting_revision"],
    validatePayload: (payload) => hasNonEmptyString(payload, "label"),
  },
  cancel_report_revision: {
    eventType: "cancel_report_revision",
    allowedStates: ["awaiting_revision"],
    validatePayload: hasOptionalPayload,
  },
  add_review_direction_after_report: {
    eventType: "add_review_direction_after_report",
    allowedStates: ["report_reviewing"],
    validatePayload: hasOptionalPayload,
  },
  submit_new_direction_after_report: {
    eventType: "submit_new_direction_after_report",
    allowedStates: ["report_reviewing"],
    validatePayload: (payload) => hasNonEmptyString(payload, "label"),
  },
  cancel_add_direction: {
    eventType: "cancel_add_direction",
    allowedStates: ["report_reviewing"],
    validatePayload: hasOptionalPayload,
  },
  enter_risk_identification: {
    eventType: "enter_risk_identification",
    allowedStates: ["report_reviewing"],
    validatePayload: hasOptionalPayload,
  },
  set_risk_decision: {
    eventType: "set_risk_decision",
    allowedStates: ["risk_identifying", "action_planning"],
    validatePayload: (payload) =>
      payload.decision === "has_risk" || payload.decision === "no_risk",
  },
  update_risk_reason: {
    eventType: "update_risk_reason",
    allowedStates: ["risk_identifying", "action_planning"],
    validatePayload: (payload) => hasNonEmptyString(payload, "label"),
  },
  resolve_no_risk: {
    eventType: "resolve_no_risk",
    allowedStates: ["risk_identifying", "action_planning"],
    validatePayload: hasOptionalPayload,
  },
  confirm_risk_identification: {
    eventType: "confirm_risk_identification",
    allowedStates: ["risk_identifying"],
    validatePayload: hasOptionalPayload,
  },
  toggle_action_item: {
    eventType: "toggle_action_item",
    allowedStates: ["action_planning"],
    validatePayload: (payload) => hasNonEmptyString(payload, "itemId"),
  },
  add_action_item: {
    eventType: "add_action_item",
    allowedStates: ["action_planning"],
    validatePayload: (payload) => hasNonEmptyString(payload, "label"),
  },
  confirm_action_plan: {
    eventType: "confirm_action_plan",
    allowedStates: ["action_planning"],
    validatePayload: hasOptionalPayload,
  },
};

export function getEventContract(
  eventType: string,
): WorkflowEventContract | undefined {
  const generatedEvent = getEventConfig(eventType);
  if (generatedEvent) {
    return {
      eventType: eventType as WorkflowEventType,
      allowedStates: (generatedEvent.allowedStates ?? []) as WorkflowState[],
      validatePayload: (payload) =>
        validatePayloadBySchema(payload, generatedEvent.payloadSchema),
    };
  }

  return workflowEventContracts[eventType as WorkflowEventType];
}

export function validateEventInput(
  state: WorkflowState,
  input: WorkflowEventInput,
): string | null {
  const contract = getEventContract(input.type);

  if (!contract) {
    return `未知事件：${input.type}`;
  }

  if (!contract.allowedStates.includes(state)) {
    return `事件“${input.type}”不属于当前阶段“${state}”`;
  }

  if (
    contract.validatePayload &&
    !contract.validatePayload(input.payload ?? {})
  ) {
    return `事件“${input.type}”的 payload 不符合契约`;
  }

  return null;
}
