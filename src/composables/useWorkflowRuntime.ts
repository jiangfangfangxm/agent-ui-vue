import { computed, ref } from "vue";
import { MockPatchPlannerModel } from "../agent/MockPatchPlannerModel";
import { RuntimePatchPlannerAgent } from "../agent/PatchPlannerAgent";
import { initialEnvelope } from "../mock/initialEnvelope";
import type {
  WorkflowEnvelope,
  WorkflowEvent,
  WorkflowEventInput,
} from "../types/workflow";
import { applyPatches, PatchApplicationError } from "../utils/patch";

function createEventId(): string {
  return `evt_${Date.now()}_${Math.random().toString(36).slice(2, 7)}`;
}

function createEvent(input: WorkflowEventInput): WorkflowEvent {
  return {
    ...input,
    id: createEventId(),
    timestamp: new Date().toLocaleTimeString([], {
      hour: "2-digit",
      minute: "2-digit",
    }),
  };
}

function createRuntimeMessage(
  id: string,
  title: string,
  body: string,
  timestamp: string,
): WorkflowEnvelope["messages"][number] {
  return {
    id,
    role: "system",
    title,
    body,
    tone: "warning",
    timestamp,
  };
}

// 当前 runtime 先接一个 mock planner，后续可以平滑替换成真实 Agent。
const patchPlanner = new RuntimePatchPlannerAgent(
  new MockPatchPlannerModel(),
);

export function useWorkflowRuntime() {
  const envelope = ref<WorkflowEnvelope>(initialEnvelope);
  const eventLog = ref<WorkflowEvent[]>([]);
  const isDispatching = ref(false);
  const lastError = ref<string | null>(null);
  const lastAppliedPatchCount = ref(0);

  const dispatchEvent = async (input: WorkflowEventInput): Promise<void> => {
    const event = createEvent(input);

    if (!envelope.value.allowedEvents.includes(event.type)) {
      lastError.value = `事件“${event.type}”在当前工作流状态下不允许执行。`;
      envelope.value = {
        ...envelope.value,
        messages: [
          createRuntimeMessage(
            `msg_blocked_${event.id}`,
            "事件已拦截",
            lastError.value,
            event.timestamp,
          ),
          ...envelope.value.messages,
        ],
      };
      return;
    }

    eventLog.value = [event, ...eventLog.value];
    isDispatching.value = true;
    lastError.value = null;
    lastAppliedPatchCount.value = 0;

    try {
      const plan = await patchPlanner.plan({
        envelope: envelope.value,
        event,
      });
      const result = applyPatches(envelope.value, plan.patches);
      envelope.value = result.envelope;
      lastAppliedPatchCount.value = result.appliedPatches.length;
    } catch (error) {
      lastError.value =
        error instanceof PatchApplicationError
          ? error.message
          : "应用 Patch 时发生了未预期的运行时错误。";

      envelope.value = {
        ...envelope.value,
        messages: [
          createRuntimeMessage(
            `msg_runtime_error_${event.id}`,
            "Patch 被拒绝",
            lastError.value,
            event.timestamp,
          ),
          ...envelope.value.messages,
        ],
      };
    } finally {
      isDispatching.value = false;
    }
  };

  return {
    envelope: computed(() => envelope.value),
    eventLog: computed(() => eventLog.value),
    isDispatching: computed(() => isDispatching.value),
    runtimeStatus: computed(() => {
      if (isDispatching.value) {
        return "dispatching";
      }

      if (lastError.value) {
        return "error";
      }

      return "idle";
    }),
    lastError: computed(() => lastError.value),
    lastAppliedPatchCount: computed(() => lastAppliedPatchCount.value),
    dispatchEvent,
  };
}
