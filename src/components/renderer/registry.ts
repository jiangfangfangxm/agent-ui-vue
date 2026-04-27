import type { Component } from "vue";
import type { WidgetType } from "../../types/workflow";
import AlertWidget from "../widgets/AlertWidget.vue";
import AuditPanelWidget from "../widgets/AuditPanelWidget.vue";
import BadgeListWidget from "../widgets/BadgeListWidget.vue";
import ButtonGroupWidget from "../widgets/ButtonGroupWidget.vue";
import ChecklistWidget from "../widgets/ChecklistWidget.vue";
import DataTableWidget from "../widgets/DataTableWidget.vue";
import KeyValueWidget from "../widgets/KeyValueWidget.vue";
import ResultSummaryWidget from "../widgets/ResultSummaryWidget.vue";
import TextWidget from "../widgets/TextWidget.vue";

export type WidgetRegistry = Record<WidgetType, Component>;

export const registry = {
  text: TextWidget,
  alert: AlertWidget,
  key_value: KeyValueWidget,
  data_table: DataTableWidget,
  badge_list: BadgeListWidget,
  checklist: ChecklistWidget,
  button_group: ButtonGroupWidget,
  result_summary: ResultSummaryWidget,
  audit_panel: AuditPanelWidget,
} satisfies WidgetRegistry;

export function resolveWidget(type: WidgetType): Component {
  return registry[type];
}
