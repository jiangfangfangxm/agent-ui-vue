<script setup lang="ts">
import type { WorkflowEventInput } from "../../types/workflow";
import { useWidgetEvents } from "./useWidgetEvents";
import type { WidgetPropsOfType } from "./widgetContract";

const props = defineProps<{
  component: WidgetPropsOfType<"button_group">["component"];
  runtime: WidgetPropsOfType<"button_group">["runtime"];
}>();

const emit = defineEmits<{
  dispatch: [event: WorkflowEventInput];
}>();

const { isEventAllowed, dispatch } = useWidgetEvents(
  props.runtime,
  emit,
  props.component.id,
);

function trigger(eventType: string, payload?: Record<string, unknown>): void {
  dispatch(eventType, payload);
}
</script>

<template>
  <div class="button-group-widget">
    <el-button
      v-for="action in component.props.actions"
      :key="`${component.id}_${action.label}`"
      :type="action.buttonType ?? 'primary'"
      size="large"
      :loading="runtime.isDispatching && isEventAllowed(action.eventType)"
      :disabled="runtime.isDispatching"
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
