<script setup lang="ts">
import type { WidgetPropsOfType } from "./widgetContract";

defineProps<WidgetPropsOfType<"alert">>();
</script>

<template>
  <el-alert
    :title="component.props.title"
    :description="component.props.description"
    :type="component.props.tone"
    show-icon
    :closable="false"
  />
</template>
