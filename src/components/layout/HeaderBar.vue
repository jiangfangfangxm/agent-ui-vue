<script setup lang="ts">
import { mapWorkflowStateLabel, mapWorkflowStateTagType } from "../../utils/labelMappers";
import type { WorkflowState } from "../../types/workflow";

defineProps<{
  title: string;
  subtitle: string;
  workflowState: WorkflowState;
  runtimeStatus: "idle" | "dispatching" | "error";
  lastAppliedPatchCount: number;
}>();
</script>

<template>
  <header class="header-bar">
    <div>
      <p class="eyebrow">智能体驱动 UI 运行时</p>
      <h1>{{ title }}</h1>
      <p class="subtitle">{{ subtitle }}</p>
    </div>

    <div class="status-group">
      <el-tag
        :type="runtimeStatus === 'error' ? 'danger' : runtimeStatus === 'dispatching' ? 'warning' : 'success'"
        effect="light"
        size="large"
      >
        运行时：{{ runtimeStatus === "dispatching" ? "处理中" : runtimeStatus === "error" ? "异常" : "空闲" }}
      </el-tag>
      <el-tag :type="mapWorkflowStateTagType(workflowState)" effect="dark" size="large">
        {{ mapWorkflowStateLabel(workflowState) }}
      </el-tag>
      <span class="patch-count">已应用 Patch：{{ lastAppliedPatchCount }}</span>
    </div>
  </header>
</template>

<style scoped>
.header-bar {
  display: flex;
  justify-content: space-between;
  gap: 24px;
  align-items: center;
  margin-bottom: 20px;
  padding: 24px 28px;
  border-radius: 24px;
  background: rgba(255, 255, 255, 0.85);
  backdrop-filter: blur(12px);
  box-shadow: 0 16px 40px rgba(17, 24, 39, 0.08);
}

.eyebrow {
  margin: 0 0 8px;
  text-transform: uppercase;
  letter-spacing: 0.12em;
  font-size: 12px;
  color: #5f6c7b;
}

h1 {
  margin: 0;
  font-size: 30px;
}

.subtitle {
  margin: 8px 0 0;
  color: #52606d;
}

.status-group {
  display: flex;
  flex-direction: column;
  align-items: flex-end;
  gap: 10px;
}

.patch-count {
  font-size: 13px;
  color: #6b7785;
}
</style>
