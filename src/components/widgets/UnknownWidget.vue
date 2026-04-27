<script setup lang="ts">
import type { WidgetProps } from "./widgetContract";

defineProps<WidgetProps<{
  id: string;
  type: string;
}>>();
</script>

<template>
  <el-empty :description="`暂不支持的组件类型：${component.type}`" />
</template>
