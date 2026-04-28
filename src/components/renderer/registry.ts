/**
 * Widget 注册表。
 * 把 Schema 中的 component type 映射到真实 Vue 组件，是 renderer 可扩展性的核心入口。
 * 新增 widget 时通常需要同时修改类型定义、具体组件实现和这里的注册关系。
 */
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
import TextInputWidget from "../widgets/TextInputWidget.vue";

export type WidgetRegistry = Record<WidgetType, Component>;

export const registry = {
  text: TextWidget,
  text_input: TextInputWidget,
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
