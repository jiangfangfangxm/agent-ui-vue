<script setup lang="ts">
import type { WidgetPropsOfType } from "./widgetContract";

defineProps<WidgetPropsOfType<"result_summary">>();
</script>

<template>
  <el-result
    :icon="component.props.status"
    :title="component.props.headline"
    :sub-title="component.props.summary"
  >
    <template #extra>
      <ul class="next-step-list">
        <li v-for="item in component.props.nextSteps" :key="item">{{ item }}</li>
      </ul>
    </template>
  </el-result>
</template>

<style scoped>
.next-step-list {
  margin: 0;
  padding-left: 18px;
  text-align: left;
  color: #52606d;
}
</style>
