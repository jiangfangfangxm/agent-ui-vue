import type { WorkflowEventInput } from "../../types/workflow";
import type { WidgetDispatch, WidgetRuntimeState } from "./widgetContract";

export function useWidgetEvents(
  getRuntime: () => WidgetRuntimeState,
  emit: (eventName: "dispatch", event: WorkflowEventInput) => void,
  componentId: string,
) {
  function isEventAllowed(eventType: string): boolean {
    return getRuntime().allowedEvents.includes(eventType);
  }

  function canDispatch(eventType: string): boolean {
    return !getRuntime().isDispatching && isEventAllowed(eventType);
  }

  function dispatch(eventType: string, payload?: Record<string, unknown>): void {
    if (!canDispatch(eventType)) {
      return;
    }

    emit("dispatch", {
      type: eventType,
      componentId,
      payload,
    });
  }

  return {
    isEventAllowed,
    canDispatch,
    dispatch: dispatch satisfies WidgetDispatch,
  };
}
