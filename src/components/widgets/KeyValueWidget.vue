<script setup lang="ts">
import { computed } from "vue";
import type { WidgetPropsOfType } from "./widgetContract";

const props = defineProps<WidgetPropsOfType<"key_value">>();

const isGridLayout = computed(
  () => props.component.props.layout === "grid",
);

const gridStyle = computed<Record<string, string>>(() => {
  if (!isGridLayout.value) {
    return {};
  }

  const minColumnWidth = props.component.props.minColumnWidth ?? 220;
  const columns = props.component.props.columns;

  if (columns && columns > 0) {
    return {
      gridTemplateColumns: `repeat(${columns}, minmax(0, 1fr))`,
    };
  }

  return {
    gridTemplateColumns: `repeat(auto-fit, minmax(${minColumnWidth}px, 1fr))`,
  };
});
</script>

<template>
  <div
    class="key-value-widget"
    :class="{ 'is-grid': isGridLayout }"
    :style="gridStyle"
  >
    <div
      v-for="item in component.props.items"
      :key="item.label"
      class="kv-row"
      :class="{ 'is-grid-row': isGridLayout }"
    >
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

.key-value-widget.is-grid {
  gap: 12px;
}

.kv-row {
  display: flex;
  justify-content: space-between;
  gap: 12px;
  padding-bottom: 10px;
  border-bottom: 1px solid #e5eaf3;
}

.kv-row.is-grid-row {
  flex-direction: column;
  justify-content: flex-start;
  padding: 14px 16px;
  border: 1px solid #e5eaf3;
  border-radius: 16px;
  background: #f7f9fc;
}

.kv-label {
  color: #6b7785;
  font-size: 13px;
}

.kv-value {
  line-height: 1.5;
}
</style>
