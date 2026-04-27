<script setup lang="ts">
import HeaderBar from "./HeaderBar.vue";
import SideMessagePanel from "./SideMessagePanel.vue";
import EventLogPanel from "./EventLogPanel.vue";
import type { WorkflowEvent, WorkflowMessage, WorkflowRiskSummary } from "../../types/workflow";

defineProps<{
  title: string;
  subtitle: string;
  workflowState: string;
  runtimeStatus: "idle" | "dispatching" | "error";
  lastError: string | null;
  lastAppliedPatchCount: number;
  messages: WorkflowMessage[];
  events: WorkflowEvent[];
  riskSummary: WorkflowRiskSummary;
}>();
</script>

<template>
  <div class="workbench-shell">
    <HeaderBar
      :title="title"
      :subtitle="subtitle"
      :workflow-state="workflowState"
      :runtime-status="runtimeStatus"
      :last-applied-patch-count="lastAppliedPatchCount"
    />

    <el-alert
      v-if="runtimeStatus === 'error' && lastError"
      class="runtime-alert"
      title="运行时 Patch 错误"
      :description="lastError"
      type="error"
      show-icon
      :closable="false"
    />

    <div class="workbench-body">
      <aside class="side-column">
        <SideMessagePanel :messages="messages" />
      </aside>

      <main class="center-column">
        <slot />
      </main>

      <aside class="side-column">
        <EventLogPanel :events="events" :risk-summary="riskSummary" />
      </aside>
    </div>
  </div>
</template>

<style scoped>
.workbench-shell {
  min-height: 100vh;
  padding: 24px;
}

.runtime-alert {
  margin-bottom: 20px;
  border-radius: 18px;
}

.workbench-body {
  display: grid;
  grid-template-columns: 280px minmax(0, 1fr) 300px;
  gap: 20px;
  align-items: start;
}

.side-column,
.center-column {
  min-width: 0;
}

@media (max-width: 1180px) {
  .workbench-body {
    grid-template-columns: 1fr;
  }
}
</style>
