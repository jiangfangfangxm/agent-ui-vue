<script setup lang="ts">
import ComponentRenderer from "./ComponentRenderer.vue";
import type { UISection, WorkflowEvent } from "../../types/workflow";

defineProps<{
  section: UISection;
  allowedEvents: string[];
  isDispatching: boolean;
}>();

const emit = defineEmits<{
  dispatch: [event: Omit<WorkflowEvent, "id" | "timestamp">];
}>();

function getComponentKey(component: UISection["components"][number]): string {
  return `${component.id}:${JSON.stringify(component.props)}`;
}
</script>

<template>
  <el-card shadow="hover" class="section-card">
    <template #header>
      <div class="section-header">
        <div>
          <h2>{{ section.title }}</h2>
          <p v-if="section.description">{{ section.description }}</p>
        </div>
      </div>
    </template>

    <div class="component-list">
      <ComponentRenderer
        v-for="component in section.components"
        :key="getComponentKey(component)"
        :component="component"
        :allowed-events="allowedEvents"
        :is-dispatching="isDispatching"
        @dispatch="emit('dispatch', $event)"
      />
    </div>
  </el-card>
</template>

<style scoped>
.section-card {
  border: none;
  border-radius: 24px;
}

.section-header h2 {
  margin: 0;
  font-size: 22px;
}

.section-header p {
  margin: 8px 0 0;
  color: #52606d;
}

.component-list {
  display: grid;
  gap: 16px;
}
</style>
