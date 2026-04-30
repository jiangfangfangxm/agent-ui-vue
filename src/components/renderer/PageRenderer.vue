<script setup lang="ts">
import SectionRenderer from "./SectionRenderer.vue";
import type {
  UIPageSchema,
  UISection,
  WorkflowEvent,
} from "../../types/workflow";

defineProps<{
  page: UIPageSchema;
  allowedEvents: string[];
  isDispatching: boolean;
}>();

const emit = defineEmits<{
  dispatch: [event: Omit<WorkflowEvent, "id" | "timestamp">];
}>();

function getSectionKey(section: UISection): string {
  return `${section.id}:${section.title}:${JSON.stringify(section.components)}`;
}
</script>

<template>
  <div class="page-renderer">
    <SectionRenderer
      v-for="section in page.sections"
      :key="getSectionKey(section)"
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
