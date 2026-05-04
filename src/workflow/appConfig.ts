import generatedAppConfig from "../../generated/warning_review_workbench/app.normalized.json";
import type { ChecklistItem, WorkflowContext, WorkflowState } from "../types/workflow";

interface PayloadPropertySchema {
  type?: string | string[];
  minLength?: number;
  enum?: string[];
}

interface PayloadSchema {
  required?: string[];
  properties?: Record<string, PayloadPropertySchema>;
}

interface GeneratedEventConfig {
  allowedStates?: string[];
  payloadSchema?: PayloadSchema;
}

interface GeneratedStateConfig {
  allowedEvents?: string[];
}

interface GeneratedContextFieldConfig {
  default?: unknown;
}

interface GeneratedModeConfig {
  allowedEvents?: string[];
}

interface GeneratedAppConfig {
  app: {
    id: string;
    entryState: string;
    initialEvent: string;
  };
  context: Record<string, GeneratedContextFieldConfig>;
  states: Record<string, GeneratedStateConfig>;
  modes?: Record<string, GeneratedModeConfig>;
  events: Record<string, GeneratedEventConfig>;
}

export const appConfig = generatedAppConfig as GeneratedAppConfig;

function clone<T>(value: T): T {
  return JSON.parse(JSON.stringify(value)) as T;
}

function getDefaultValue<T>(field: string, fallback: T): T {
  const value = appConfig.context[field]?.default;
  return value === undefined ? fallback : clone(value as T);
}

export function createContextFromAppConfig(): WorkflowContext {
  return {
    warningDetailItems: getDefaultValue("warningDetailItems", []),
    reviewDirections: getDefaultValue<ChecklistItem[]>("reviewDirections", []),
    reportText: getDefaultValue("reportText", ""),
    riskDecision: getDefaultValue("riskDecision", undefined),
    riskReason: getDefaultValue("riskReason", ""),
    actionItems: getDefaultValue<ChecklistItem[]>("actionItems", []),
  };
}

export function getAllowedEventsFromAppConfig(
  state: WorkflowState,
  options?: { mode?: string; includeRiskControls?: boolean },
): string[] {
  if (options?.mode) {
    return [...(appConfig.modes?.[options.mode]?.allowedEvents ?? [])];
  }

  const events = [...(appConfig.states[state]?.allowedEvents ?? ["open_detail"])];
  if (state === "action_planning" && options?.includeRiskControls) {
    return [
      ...new Set([
        "set_risk_decision",
        "update_risk_reason",
        "resolve_no_risk",
        ...events,
      ]),
    ];
  }

  return [...new Set(events)];
}

export function getEventConfig(eventType: string): GeneratedEventConfig | undefined {
  return appConfig.events[eventType];
}

function hasNonEmptyString(
  payload: Record<string, unknown>,
  key: string,
): boolean {
  return typeof payload[key] === "string" && payload[key].trim().length > 0;
}

export function validatePayloadBySchema(
  payload: Record<string, unknown>,
  schema: PayloadSchema = {},
): boolean {
  const required = schema.required ?? [];
  const properties = schema.properties ?? {};

  for (const field of required) {
    const property = properties[field] ?? {};
    if ((property.minLength ?? 0) >= 1 || property.type === "string") {
      if (!hasNonEmptyString(payload, field)) {
        return false;
      }
      continue;
    }

    if (payload[field] === undefined) {
      return false;
    }
  }

  for (const [field, property] of Object.entries(properties)) {
    if (property.enum && payload[field] !== undefined) {
      if (!property.enum.includes(String(payload[field]))) {
        return false;
      }
    }
  }

  return true;
}
