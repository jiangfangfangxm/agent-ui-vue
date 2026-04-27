<script setup lang="ts">
import { computed } from "vue";
import { resolveWidget } from "./registry";
import UnknownWidget from "../widgets/UnknownWidget.vue";
import type { UIComponent, WorkflowEvent } from "../../types/workflow";
import type { WidgetRuntimeState } from "../widgets/widgetContract";

const props = defineProps<{
  component: UIComponent;
  allowedEvents: string[];
  isDispatching: boolean;
}>();

const emit = defineEmits<{
  dispatch: [event: Omit<WorkflowEvent, "id" | "timestamp">];
}>();

const runtime = computed<WidgetRuntimeState>(() => ({
  allowedEvents: props.allowedEvents,
  isDispatching: props.isDispatching,
}));

const resolvedComponent = computed(
  () => resolveWidget(props.component.type) ?? UnknownWidget,
);
</script>

<template>
  <component
    :is="resolvedComponent"
    :component="component"
    :runtime="runtime"
    @dispatch="emit('dispatch', $event)"
  />
</template>
