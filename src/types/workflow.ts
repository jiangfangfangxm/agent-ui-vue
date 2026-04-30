/**
 * 项目核心协议定义。
 * 这里描述运行时共享的数据模型，包括 Schema、Event、Patch 和 Envelope。
 * 维护时优先在这里统一收敛类型，而不是让各层各自发明字段。
 */
export type WidgetType =
  | "text"
  | "text_input"
  | "alert"
  | "key_value"
  | "data_table"
  | "badge_list"
  | "checklist"
  | "button_group"
  | "result_summary"
  | "audit_panel";

export interface WorkflowMessage {
  id: string;
  role: "agent" | "system" | "user";
  title: string;
  body: string;
  tone?: "info" | "success" | "warning" | "danger";
  timestamp: string;
}

export interface WorkflowRiskSummary {
  level: RiskLevel;
  summary: string;
  details: string[];
}

export type RiskLevel = "low" | "medium" | "high";
export type WorkflowState =
  | "reviewing"
  | "report_reviewing"
  | "risk_identifying"
  | "action_planning"
  | "resolved_no_risk"
  | "resolved_with_action"
  | "presenting_result"
  | "awaiting_revision";

export interface WorkflowEvent {
  id: string;
  type: string;
  componentId: string;
  payload?: Record<string, unknown>;
  timestamp: string;
}

export type WorkflowEventInput = Omit<WorkflowEvent, "id" | "timestamp">;

export interface EventAction {
  eventType: string;
  label: string;
  payload?: Record<string, unknown>;
  buttonType?: "primary" | "success" | "warning" | "danger" | "info";
}

export interface ChecklistItem {
  id: string;
  label: string;
  description?: string;
  checked: boolean;
}

export interface AuditRecord {
  label: string;
  value: string;
  status?: "success" | "warning" | "danger" | "info";
}

interface BaseComponent<T extends WidgetType, P> {
  id: string;
  type: T;
  title?: string;
  props: P;
}

export type TextComponent = BaseComponent<
  "text",
  {
    content: string;
    variant?: "body" | "title" | "caption";
  }
>;

export type AlertComponent = BaseComponent<
  "alert",
  {
    title: string;
    description: string;
    tone: "success" | "info" | "warning" | "error";
  }
>;

export type TextInputComponent = BaseComponent<
  "text_input",
  {
    eventType: string;
    label?: string;
    placeholder?: string;
    buttonLabel?: string;
    helperText?: string;
    clearOnSubmit?: boolean;
  }
>;

export type KeyValueComponent = BaseComponent<
  "key_value",
  {
    layout?: "stack" | "grid";
    columns?: number;
    minColumnWidth?: number;
    items: Array<{ label: string; value: string }>;
  }
>;

export interface DataTableColumn {
  key: string;
  label: string;
  type?: "text" | "number" | "boolean" | "tag" | "link" | "date" | "action";
  width?: number | string;
  minWidth?: number | string;
  align?: "left" | "center" | "right";
  format?: "plain" | "percent" | "currency" | "datetime" | "short-date";
  currency?: string;
  truncate?: boolean;
  multiline?: boolean;
  tagMap?: Record<
    string,
    {
      label?: string;
      tone?: "success" | "info" | "warning" | "danger";
    }
  >;
  booleanLabels?: {
    trueLabel?: string;
    falseLabel?: string;
  };
  actions?: DataTableAction[];
}

export type DataTableRow = Record<
  string,
  string | number | boolean | null | undefined
>;

export interface DataTableAction {
  label: string;
  eventType: string;
  buttonType?: "primary" | "success" | "warning" | "danger" | "info";
  payload?: Record<string, unknown>;
  rowFieldMap?: Record<string, string>;
}

export type DataTableComponent = BaseComponent<
  "data_table",
  {
    columns: DataTableColumn[];
    rows: DataTableRow[];
    stripe?: boolean;
    border?: boolean;
    size?: "large" | "default" | "small";
    emptyText?: string;
  }
>;

export type BadgeListComponent = BaseComponent<
  "badge_list",
  {
    items: string[];
    tone?: "success" | "info" | "warning" | "danger";
  }
>;

export type ChecklistComponent = BaseComponent<
  "checklist",
  {
    items: ChecklistItem[];
    action: {
      eventType: string;
    };
  }
>;

export type ButtonGroupComponent = BaseComponent<
  "button_group",
  {
    actions: EventAction[];
  }
>;

export type ResultSummaryComponent = BaseComponent<
  "result_summary",
  {
    status: "success" | "warning" | "error" | "info";
    headline: string;
    summary: string;
    nextSteps: string[];
  }
>;

export type AuditPanelComponent = BaseComponent<
  "audit_panel",
  {
    records: AuditRecord[];
  }
>;

export type UIComponent =
  | TextComponent
  | TextInputComponent
  | AlertComponent
  | KeyValueComponent
  | DataTableComponent
  | BadgeListComponent
  | ChecklistComponent
  | ButtonGroupComponent
  | ResultSummaryComponent
  | AuditPanelComponent;

export interface UIComponentMap {
  text: TextComponent;
  text_input: TextInputComponent;
  alert: AlertComponent;
  key_value: KeyValueComponent;
  data_table: DataTableComponent;
  badge_list: BadgeListComponent;
  checklist: ChecklistComponent;
  button_group: ButtonGroupComponent;
  result_summary: ResultSummaryComponent;
  audit_panel: AuditPanelComponent;
}

export type UIComponentOfType<T extends WidgetType> = UIComponentMap[T];

export interface UISection {
  id: string;
  title: string;
  description?: string;
  components: UIComponent[];
}

export interface UIPageSchema {
  id: string;
  title: string;
  description: string;
  sections: UISection[];
}

export interface WorkflowEnvelope {
  id: string;
  version: string;
  state: WorkflowState;
  page: UIPageSchema;
  messages: WorkflowMessage[];
  allowedEvents: string[];
  riskSummary: WorkflowRiskSummary;
}

export type PatchOperation =
  | { op: "set_state"; value: WorkflowState }
  | { op: "replace_section"; sectionId: string; value: UISection }
  | { op: "append_section"; value: UISection; beforeSectionId?: string }
  | { op: "remove_section"; sectionId: string }
  | { op: "prepend_message"; value: WorkflowMessage }
  | { op: "set_allowed_events"; value: string[] }
  | { op: "set_risk_summary"; value: WorkflowRiskSummary };

export interface PatchExecutionResult {
  envelope: WorkflowEnvelope;
  appliedPatches: PatchOperation[];
}
