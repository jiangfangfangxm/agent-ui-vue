<script setup lang="ts">
import { computed } from "vue";
import type {
  DataTableAction,
  DataTableColumn,
  DataTableRow,
  WorkflowEventInput,
} from "../../types/workflow";
import type { WidgetPropsOfType } from "./widgetContract";
import { useWidgetEvents } from "./useWidgetEvents";

const props = defineProps<WidgetPropsOfType<"data_table">>();

const emit = defineEmits<{
  dispatch: [event: WorkflowEventInput];
}>();

const { isEventAllowed, dispatch } = useWidgetEvents(
  props.runtime,
  emit,
  props.component.id,
);

const tableColumns = computed(() => props.component.props.columns);

function getCellValue(row: DataTableRow, key: string) {
  return row[key];
}

function formatDate(value: string | number): string {
  const date = new Date(value);

  if (Number.isNaN(date.getTime())) {
    return String(value);
  }

  return date.toLocaleString("zh-CN", {
    year: "numeric",
    month: "2-digit",
    day: "2-digit",
    hour: "2-digit",
    minute: "2-digit",
  });
}

function formatShortDate(value: string | number): string {
  const date = new Date(value);

  if (Number.isNaN(date.getTime())) {
    return String(value);
  }

  return date.toLocaleDateString("zh-CN", {
    year: "numeric",
    month: "2-digit",
    day: "2-digit",
  });
}

function formatCurrency(value: number, currency = "CNY"): string {
  return new Intl.NumberFormat("zh-CN", {
    style: "currency",
    currency,
  }).format(value);
}

function formatPercent(value: number): string {
  return new Intl.NumberFormat("zh-CN", {
    style: "percent",
    maximumFractionDigits: 2,
  }).format(value);
}

function formatCellValue(row: DataTableRow, column: DataTableColumn): string {
  const value = getCellValue(row, column.key);

  if (value === null || value === undefined || value === "") {
    return "-";
  }

  if (column.type === "boolean" && typeof value === "boolean") {
    return value
      ? column.booleanLabels?.trueLabel ?? "是"
      : column.booleanLabels?.falseLabel ?? "否";
  }

  if (column.format === "percent" && typeof value === "number") {
    return formatPercent(value);
  }

  if (column.format === "currency" && typeof value === "number") {
    return formatCurrency(value, column.currency);
  }

  if (
    (column.type === "date" || column.format === "datetime") &&
    (typeof value === "string" || typeof value === "number")
  ) {
    return formatDate(value);
  }

  if (
    column.format === "short-date" &&
    (typeof value === "string" || typeof value === "number")
  ) {
    return formatShortDate(value);
  }

  return String(value);
}

function resolveTag(
  row: DataTableRow,
  column: DataTableColumn,
): { label: string; tone: "success" | "info" | "warning" | "danger" } {
  const raw = String(getCellValue(row, column.key) ?? "");
  const mapped = column.tagMap?.[raw];

  return {
    label: mapped?.label ?? (raw || "-"),
    tone: mapped?.tone ?? "info",
  };
}

function resolveActionPayload(
  row: DataTableRow,
  action: DataTableAction,
): Record<string, unknown> {
  const mappedPayload = Object.entries(action.rowFieldMap ?? {}).reduce<
    Record<string, unknown>
  >((payload, [payloadKey, rowField]) => {
    payload[payloadKey] = row[rowField];
    return payload;
  }, {});

  return {
    ...mappedPayload,
    ...(action.payload ?? {}),
  };
}

function triggerAction(row: DataTableRow, action: DataTableAction): void {
  dispatch(action.eventType, resolveActionPayload(row, action));
}

function getCellClass(column: DataTableColumn): string[] {
  const classes = ["cell-value"];

  if (column.truncate) {
    classes.push("is-truncated");
  }

  if (column.multiline) {
    classes.push("is-multiline");
  }

  return classes;
}
</script>

<template>
  <div class="data-table-widget">
    <el-table
      :data="component.props.rows"
      :border="component.props.border ?? true"
      :stripe="component.props.stripe ?? true"
      :size="component.props.size ?? 'default'"
      :empty-text="component.props.emptyText ?? '暂无表格数据'"
      class="table-surface"
    >
      <el-table-column
        v-for="column in tableColumns"
        :key="column.key"
        :prop="column.key"
        :label="column.label"
        :width="column.width"
        :min-width="column.minWidth"
        :align="column.align ?? (column.type === 'number' ? 'right' : column.type === 'boolean' || column.type === 'tag' ? 'center' : 'left')"
      >
        <template #default="{ row }">
          <div v-if="column.type === 'action'" class="action-group">
            <el-button
              v-for="action in column.actions ?? []"
              :key="`${column.key}_${action.label}`"
              :type="action.buttonType ?? 'primary'"
              size="small"
              :disabled="props.runtime.isDispatching || !isEventAllowed(action.eventType)"
              @click="triggerAction(row, action)"
            >
              {{ action.label }}
            </el-button>
          </div>

          <el-tag
            v-else-if="column.type === 'tag'"
            :type="resolveTag(row, column).tone"
            effect="light"
            round
          >
            {{ resolveTag(row, column).label }}
          </el-tag>

          <el-link
            v-else-if="column.type === 'link'"
            :href="String(getCellValue(row, column.key) ?? '#')"
            type="primary"
            target="_blank"
            :underline="false"
          >
            {{ formatCellValue(row, column) }}
          </el-link>

          <span v-else :class="getCellClass(column)">
            {{ formatCellValue(row, column) }}
          </span>
        </template>
      </el-table-column>
    </el-table>
  </div>
</template>

<style scoped>
.data-table-widget {
  width: 100%;
}

.table-surface {
  width: 100%;
  border-radius: 16px;
  overflow: hidden;
}

.cell-value {
  display: inline-block;
  line-height: 1.5;
  word-break: break-word;
}

.cell-value.is-truncated {
  max-width: 100%;
  overflow: hidden;
  text-overflow: ellipsis;
  white-space: nowrap;
}

.cell-value.is-multiline {
  white-space: normal;
  word-break: break-word;
}

.action-group {
  display: flex;
  gap: 8px;
  flex-wrap: wrap;
}
</style>
