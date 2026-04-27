<script setup lang="ts">
import type { WorkflowMessage } from "../../types/workflow";

defineProps<{
  messages: WorkflowMessage[];
}>();

function mapTone(tone?: WorkflowMessage["tone"]): string {
  switch (tone) {
    case "success":
      return "success";
    case "warning":
      return "warning";
    case "danger":
      return "danger";
    default:
      return "info";
  }
}
</script>

<template>
  <el-card shadow="hover" class="panel-card">
    <template #header>
      <div class="panel-header">消息面板</div>
    </template>

    <div class="message-list">
      <el-alert
        v-for="message in messages"
        :key="message.id"
        :title="message.title"
        :type="mapTone(message.tone)"
        :description="`${message.body} · ${message.timestamp}`"
        show-icon
        :closable="false"
      />
    </div>
  </el-card>
</template>

<style scoped>
.panel-card {
  border: none;
  border-radius: 20px;
}

.panel-header {
  font-weight: 700;
}

.message-list {
  display: grid;
  gap: 12px;
}
</style>
