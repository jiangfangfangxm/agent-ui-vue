<script setup lang="ts">
import type { WidgetPropsOfType } from "./widgetContract";

defineProps<WidgetPropsOfType<"badge_list">>();
</script>

<template>
  <div class="badge-list-widget">
    <el-tag
      v-for="item in component.props.items"
      :key="item"
      :type="component.props.tone ?? 'info'"
      effect="light"
      round
    >
      {{ item }}
    </el-tag>
  </div>
</template>

<style scoped>
.badge-list-widget {
  display: flex;
  gap: 10px;
  flex-wrap: wrap;
}
</style>
