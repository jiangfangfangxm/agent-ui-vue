<script setup lang="ts">
import type { WidgetPropsOfType } from "./widgetContract";

defineProps<WidgetPropsOfType<"audit_panel">>();

function mapTagType(status?: string): "success" | "warning" | "danger" | "info" {
  switch (status) {
    case "success":
      return "success";
    case "warning":
      return "warning";
    case "danger":
      return "danger";
    default:
      return "info";
  }
}
</script>

<template>
  <div class="audit-widget">
    <div v-for="record in component.props.records" :key="record.label" class="audit-row">
      <div>
        <strong>{{ record.label }}</strong>
        <p>{{ record.value }}</p>
      </div>
      <el-tag :type="mapTagType(record.status)">
        {{ record.status ?? "info" }}
      </el-tag>
    </div>
  </div>
</template>

<style scoped>
.audit-widget {
  display: grid;
  gap: 12px;
}

.audit-row {
  display: flex;
  justify-content: space-between;
  gap: 12px;
  align-items: center;
  padding: 14px 16px;
  border-radius: 16px;
  background: #f7f9fc;
}

.audit-row p {
  margin: 6px 0 0;
  color: #6b7785;
}
</style>
