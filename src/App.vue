<script setup lang="ts">
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
  >
    <PageRenderer
      :page="envelope.page"
      :allowed-events="envelope.allowedEvents"
      :is-dispatching="isDispatching"
      @dispatch="dispatchEvent"
    />
  </WorkbenchLayout>
</template>
