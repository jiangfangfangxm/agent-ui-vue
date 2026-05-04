<script setup lang="ts">
import { computed, onMounted, ref } from "vue";
import BusinessConfigTool from "./components/config/BusinessConfigTool.vue";
import WorkbenchLayout from "./components/layout/WorkbenchLayout.vue";
import PageRenderer from "./components/renderer/PageRenderer.vue";
import { useWorkflowRuntime } from "./composables/useWorkflowRuntime";

type AppMode = "runtime" | "config";

const appMode = ref<AppMode>("runtime");

const {
  envelope,
  eventLog,
  isDispatching,
  runtimeStatus,
  lastError,
  lastAppliedPatchCount,
  dispatchEvent,
} = useWorkflowRuntime();

const actionPlanDebug = computed(() => {
  const section = envelope.value.page.sections.find(
    (item) => item.id === "sec_action_plan",
  );
  const checklist = section?.components.find(
    (item) => item.type === "checklist",
  );
  const items =
    checklist?.type === "checklist" ? checklist.props.items : [];

  return {
    count: items.length,
    checkedCount: items.filter((item) => item.checked).length,
    labels: items.map((item) => item.label),
  };
});

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
  <div class="app-mode-switch">
    <el-segmented
      v-model="appMode"
      :options="[
        { label: '运行台', value: 'runtime' },
        { label: '配置工具', value: 'config' },
      ]"
    />
  </div>

  <BusinessConfigTool v-if="appMode === 'config'" />

  <WorkbenchLayout
    v-else
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
    :action-plan-debug="actionPlanDebug"
  >
    <PageRenderer
      :page="envelope.page"
      :allowed-events="envelope.allowedEvents"
      :is-dispatching="isDispatching"
      @dispatch="dispatchEvent"
    />
  </WorkbenchLayout>
</template>

<style scoped>
.app-mode-switch {
  position: fixed;
  top: 18px;
  right: 24px;
  z-index: 40;
  padding: 6px;
  border: 1px solid #dbe4ef;
  border-radius: 8px;
  background: rgb(255 255 255 / 94%);
  box-shadow: 0 10px 24px rgb(15 23 42 / 0.10);
}
</style>
