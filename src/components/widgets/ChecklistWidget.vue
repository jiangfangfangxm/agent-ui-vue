<script setup lang="ts">
import type { WorkflowEventInput } from "../../types/workflow";
import { useWidgetEvents } from "./useWidgetEvents";
import type { WidgetPropsOfType } from "./widgetContract";

const props = defineProps<{
  component: WidgetPropsOfType<"checklist">["component"];
  runtime: WidgetPropsOfType<"checklist">["runtime"];
}>();

const emit = defineEmits<{
  dispatch: [event: WorkflowEventInput];
}>();

const { canDispatch, dispatch } = useWidgetEvents(
  () => props.runtime,
  emit,
  props.component.id,
);

function toggle(itemId: string): void {
  dispatch(props.component.props.action.eventType, { itemId });
}
</script>

<template>
  <div class="checklist-widget">
    <label
      v-for="item in component.props.items"
      :key="item.id"
      class="check-item"
    >
      <el-checkbox
        :model-value="item.checked"
        :disabled="!canDispatch(component.props.action.eventType)"
        @update:model-value="toggle(item.id)"
      >
        <span class="check-label">{{ item.label }}</span>
      </el-checkbox>
      <p v-if="item.description">{{ item.description }}</p>
    </label>
  </div>
</template>

<style scoped>
.checklist-widget {
  display: grid;
  gap: 14px;
}

.check-item {
  display: grid;
  gap: 6px;
  padding: 14px 16px;
  border-radius: 16px;
  background: #f7f9fc;
}

.check-label {
  font-weight: 600;
}

.check-item p {
  margin: 0 0 0 24px;
  color: #6b7785;
}
</style>
