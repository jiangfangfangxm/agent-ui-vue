<script setup lang="ts">
import type { WidgetPropsOfType } from "./widgetContract";

defineProps<WidgetPropsOfType<"key_value">>();
</script>

<template>
  <div class="key-value-widget">
    <div v-for="item in component.props.items" :key="item.label" class="kv-row">
      <span class="kv-label">{{ item.label }}</span>
      <strong class="kv-value">{{ item.value }}</strong>
    </div>
  </div>
</template>

<style scoped>
.key-value-widget {
  display: grid;
  gap: 10px;
}

.kv-row {
  display: flex;
  justify-content: space-between;
  gap: 12px;
  padding-bottom: 10px;
  border-bottom: 1px solid #e5eaf3;
}

.kv-label {
  color: #6b7785;
}
</style>
