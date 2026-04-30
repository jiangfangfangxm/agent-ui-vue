<script setup lang="ts">
import type { WorkflowEventInput } from "../../types/workflow";
import type { WidgetPropsOfType } from "./widgetContract";

const props = defineProps<{
  component: WidgetPropsOfType<"button_group">["component"];
  runtime: WidgetPropsOfType<"button_group">["runtime"];
}>();

const emit = defineEmits<{
  dispatch: [event: WorkflowEventInput];
}>();

function isEventAllowed(eventType: string): boolean {
  return props.runtime.allowedEvents.includes(eventType);
}

function canDispatch(eventType: string): boolean {
  return !props.runtime.isDispatching && isEventAllowed(eventType);
}

function trigger(eventType: string, payload?: Record<string, unknown>): void {
  if (!canDispatch(eventType)) {
    return;
  }

  emit("dispatch", {
    type: eventType,
    componentId: props.component.id,
    payload,
  });
}

function isActionLoading(eventType: string): boolean {
  return props.runtime.isDispatching && isEventAllowed(eventType);
}
</script>

<template>
  <div class="button-group-widget">
    <el-button
      v-for="action in component.props.actions"
      :key="`${component.id}_${action.label}`"
      :type="action.buttonType ?? 'primary'"
      size="large"
      :loading="isActionLoading(action.eventType)"
      :disabled="!canDispatch(action.eventType)"
      @click="trigger(action.eventType, action.payload)"
    >
      {{ action.label }}
    </el-button>
  </div>
</template>

<style scoped>
.button-group-widget {
  display: flex;
  gap: 12px;
  flex-wrap: wrap;
}
</style>
