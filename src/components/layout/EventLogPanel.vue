<script setup lang="ts">
import { mapRiskLevelLabel, mapRiskLevelTagType } from "../../utils/labelMappers";
import type { WorkflowEvent, WorkflowRiskSummary } from "../../types/workflow";

defineProps<{
  events: WorkflowEvent[];
  riskSummary: WorkflowRiskSummary;
}>();
</script>

<template>
  <div class="event-panel">
    <el-card shadow="hover" class="panel-card">
      <template #header>
        <div class="panel-header">风险摘要</div>
      </template>

      <el-tag :type="mapRiskLevelTagType(riskSummary.level)">
        {{ mapRiskLevelLabel(riskSummary.level) }}
      </el-tag>
      <p class="summary-copy">{{ riskSummary.summary }}</p>
      <ul class="summary-list">
        <li v-for="detail in riskSummary.details" :key="detail">
          {{ detail }}
        </li>
      </ul>
    </el-card>

    <el-card shadow="hover" class="panel-card">
      <template #header>
        <div class="panel-header">事件日志</div>
      </template>

      <el-empty v-if="!events.length" description="暂时还没有事件" />

      <div v-else class="event-list">
        <div v-for="event in events" :key="event.id" class="event-item">
          <div class="event-topline">
            <strong>{{ event.type }}</strong>
            <span>{{ event.timestamp }}</span>
          </div>
          <p>{{ event.componentId }}</p>
        </div>
      </div>
    </el-card>
  </div>
</template>

<style scoped>
.event-panel {
  display: grid;
  gap: 16px;
}

.panel-card {
  border: none;
  border-radius: 20px;
}

.panel-header {
  font-weight: 700;
}

.summary-copy {
  margin: 12px 0;
  color: #52606d;
}

.summary-list {
  margin: 0;
  padding-left: 18px;
  color: #52606d;
}

.event-list {
  display: grid;
  gap: 12px;
}

.event-item {
  padding: 12px;
  border-radius: 14px;
  background: #f7f9fc;
}

.event-topline {
  display: flex;
  justify-content: space-between;
  gap: 12px;
}

.event-item p {
  margin: 8px 0 0;
  color: #52606d;
}
</style>
