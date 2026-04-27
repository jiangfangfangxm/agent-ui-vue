import { MockPatchPlannerModel } from "../agent/MockPatchPlannerModel";
import type { PatchOperation, WorkflowEnvelope, WorkflowEvent } from "../types/workflow";

// Compatibility wrapper for older callers that still expect a plain patch engine.
export async function mockPatchEngine(
  envelope: WorkflowEnvelope,
  event: WorkflowEvent,
): Promise<PatchOperation[]> {
  const planner = new MockPatchPlannerModel();
  const plan = await planner.generate({
    envelope,
    event,
  });

  return plan.patches;
}
