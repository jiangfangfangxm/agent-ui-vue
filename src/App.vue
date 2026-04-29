<script setup lang="ts">
import { onMounted } from "vue";
import WorkbenchLayout from "./components/layout/WorkbenchLayout.vue";
import PageRenderer from "./components/renderer/PageRenderer.vue";
import { useWorkflowRuntime } from "./composables/useWorkflowRuntime";

const {
  envelope,
  eventLog,
  isDispatching,
  runtimeStatus,
  lastError,
  lastAppliedPatchCount,
  dispatchEvent,
} = useWorkflowRuntime();

onMounted(() => {
  if (!envelope.value.allowedEvents.includes("init_event")) {
    return;
  }

  void dispatchEvent({
    type: "init_event",
    componentId: "system_init",
  });
});
</script>

<template>
  <WorkbenchLayout
    :title="envelope.page.title"
    :subtitle="envelope.page.description"
    :workflow-state="envelope.state"
    :runtime-status="runtimeStatus"
    :last-error="lastError"
    :last-applied-patch-count="lastAppliedPatchCount"
    :messages="envelope.messages"
    :events="eventLog"
    :risk-summary="envelope.riskSummary"
    :allowed-events="envelope.allowedEvents"
  >
    <PageRenderer
      :page="envelope.page"
      :allowed-events="envelope.allowedEvents"
      :is-dispatching="isDispatching"
      @dispatch="dispatchEvent"
    />
  </WorkbenchLayout>
</template>
