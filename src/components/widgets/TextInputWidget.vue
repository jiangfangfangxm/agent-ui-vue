<script setup lang="ts">
import { computed, ref } from "vue";
import type { WorkflowEventInput } from "../../types/workflow";
import type { WidgetPropsOfType } from "./widgetContract";
import { useWidgetEvents } from "./useWidgetEvents";

const props = defineProps<{
  component: WidgetPropsOfType<"text_input">["component"];
  runtime: WidgetPropsOfType<"text_input">["runtime"];
}>();

const emit = defineEmits<{
  dispatch: [event: WorkflowEventInput];
}>();

const draft = ref("");
const { canDispatch, dispatch } = useWidgetEvents(
  () => props.runtime,
  emit,
  props.component.id,
);

const normalizedValue = computed(() => draft.value.trim());
const canSubmit = computed(
  () =>
    normalizedValue.value.length > 0 &&
    canDispatch(props.component.props.eventType),
);

function submit(): void {
  if (!canSubmit.value) {
    return;
  }

  dispatch(props.component.props.eventType, {
    label: normalizedValue.value,
  });

  if (props.component.props.clearOnSubmit ?? true) {
    draft.value = "";
  }
}
</script>

<template>
  <div class="text-input-widget">
    <div class="input-head">
      <label v-if="component.props.label" class="input-label">
        {{ component.props.label }}
      </label>
      <p v-if="component.props.helperText" class="input-helper">
        {{ component.props.helperText }}
      </p>
    </div>

    <div class="input-row">
      <el-input
        v-model="draft"
        :placeholder="component.props.placeholder ?? '请输入内容'"
        :disabled="runtime.isDispatching"
        clearable
        @keyup.enter="submit"
      />
      <el-button
        type="primary"
        :disabled="!canSubmit"
        :loading="runtime.isDispatching"
        @click="submit"
      >
        {{ component.props.buttonLabel ?? "提交" }}
      </el-button>
    </div>
  </div>
</template>

<style scoped>
.text-input-widget {
  display: grid;
  gap: 10px;
  padding: 16px;
  border-radius: 16px;
  background: #f7f9fc;
}

.input-head {
  display: grid;
  gap: 4px;
}

.input-label {
  font-size: 14px;
  font-weight: 600;
  color: #1f2a37;
}

.input-helper {
  margin: 0;
  font-size: 13px;
  color: #6b7785;
}

.input-row {
  display: grid;
  grid-template-columns: minmax(0, 1fr) auto;
  gap: 12px;
  align-items: center;
}

@media (max-width: 768px) {
  .input-row {
    grid-template-columns: 1fr;
  }
}
</style>
