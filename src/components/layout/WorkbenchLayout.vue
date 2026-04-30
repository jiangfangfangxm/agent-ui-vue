<script setup lang="ts">
import HeaderBar from "./HeaderBar.vue";
import SideMessagePanel from "./SideMessagePanel.vue";
import EventLogPanel from "./EventLogPanel.vue";
import type {
  WorkflowEvent,
  WorkflowMessage,
  WorkflowRiskSummary,
  WorkflowState,
} from "../../types/workflow";

defineProps<{
  title: string;
  subtitle: string;
  workflowState: WorkflowState;
  runtimeStatus: "idle" | "dispatching" | "error";
  lastError: string | null;
  lastAppliedPatchCount: number;
  messages: WorkflowMessage[];
  events: WorkflowEvent[];
  riskSummary: WorkflowRiskSummary;
  allowedEvents: string[];
  actionPlanDebug: {
    count: number;
    checkedCount: number;
    labels: string[];
  };
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

    <div class="debug-allowed-events">
      <p class="debug-title">Allowed Events</p>
      <div class="debug-tags">
        <el-tag
          v-for="eventType in allowedEvents"
          :key="eventType"
          size="small"
          type="info"
          effect="plain"
        >
          {{ eventType }}
        </el-tag>
        <span v-if="allowedEvents.length === 0" class="debug-empty">none</span>
      </div>
      <div class="debug-divider" />
      <p class="debug-title">Action Plan Debug</p>
      <p class="debug-line">
        count: {{ actionPlanDebug.count }} / checked: {{ actionPlanDebug.checkedCount }}
      </p>
      <p class="debug-line">
        labels:
        {{ actionPlanDebug.labels.length ? actionPlanDebug.labels.join("、") : "none" }}
      </p>
    </div>
  </div>
</template>

<style scoped>
.workbench-shell {
  min-height: 100vh;
  padding: 24px;
  padding-bottom: 160px;
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

.debug-allowed-events {
  position: fixed;
  right: 20px;
  bottom: 20px;
  z-index: 20;
  max-width: min(420px, calc(100vw - 40px));
  padding: 12px 14px;
  border: 1px solid #d6deeb;
  border-radius: 16px;
  background: rgb(255 255 255 / 92%);
  backdrop-filter: blur(10px);
  box-shadow: 0 10px 24px rgb(15 23 42 / 0.10);
}

.debug-title {
  margin: 0 0 10px;
  font-size: 12px;
  font-weight: 700;
  letter-spacing: 0.04em;
  color: #52606d;
  text-transform: uppercase;
}

.debug-tags {
  display: flex;
  flex-wrap: wrap;
  gap: 8px;
}

.debug-divider {
  height: 1px;
  margin: 12px 0 10px;
  background: #e5ebf5;
}

.debug-line {
  margin: 4px 0 0;
  font-size: 12px;
  line-height: 1.5;
  color: #52606d;
  word-break: break-word;
}

.debug-empty {
  font-size: 13px;
  color: #8a97a6;
}

.side-column,
.center-column {
  min-width: 0;
}

@media (max-width: 1180px) {
  .workbench-body {
    grid-template-columns: 1fr;
  }

  .debug-allowed-events {
    left: 20px;
    right: 20px;
    bottom: 16px;
    max-width: none;
  }
}
</style>
