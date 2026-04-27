<script setup lang="ts">
import type { WidgetPropsOfType } from "./widgetContract";

defineProps<WidgetPropsOfType<"text">>();
</script>

<template>
  <div class="text-widget" :data-variant="component.props.variant ?? 'body'">
    {{ component.props.content }}
  </div>
</template>

<style scoped>
.text-widget {
  color: #23303f;
  line-height: 1.7;
}

.text-widget[data-variant="title"] {
  font-size: 24px;
  font-weight: 700;
}

.text-widget[data-variant="caption"] {
  font-size: 13px;
  color: #6b7785;
}
</style>
