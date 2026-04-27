<script setup lang="ts">
import SectionRenderer from "./SectionRenderer.vue";
import type { UIPageSchema, WorkflowEvent } from "../../types/workflow";

defineProps<{
  page: UIPageSchema;
  allowedEvents: string[];
  isDispatching: boolean;
}>();

const emit = defineEmits<{
  dispatch: [event: Omit<WorkflowEvent, "id" | "timestamp">];
}>();
</script>

<template>
  <div class="page-renderer">
    <SectionRenderer
      v-for="section in page.sections"
      :key="section.id"
      :section="section"
      :allowed-events="allowedEvents"
      :is-dispatching="isDispatching"
      @dispatch="emit('dispatch', $event)"
    />
  </div>
</template>

<style scoped>
.page-renderer {
  display: grid;
  gap: 18px;
}
</style>
