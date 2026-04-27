import type {
  PatchOperation,
  PatchExecutionResult,
  WorkflowEnvelope,
} from "../types/workflow";
import {
  applyPatches,
  PatchApplicationError,
} from "../utils/patch";
import type { PatchPlanningOutput } from "./contracts";

/**
 * Patch 计划的校验结果。
 * simulatedResult 表示在当前 envelope 上试运行 patch 后得到的结果。
 */
export interface PatchPlanValidationResult {
  ok: boolean;
  errors: string[];
  simulatedResult?: PatchExecutionResult;
}

function validateRationale(rationale: string): string[] {
  return rationale.trim()
    ? []
    : ["Patch 计划必须包含非空的 rationale，用于解释状态迁移原因。"];
}

function validatePatchList(patches: PatchOperation[]): string[] {
  if (!patches.length) {
    return ["Patch 计划至少需要包含一个 patch 操作。"];
  }

  return [];
}

/**
 * 在真正应用 patch 之前，先做一次结构校验和试运行。
 */
export function validatePatchPlan(
  envelope: WorkflowEnvelope,
  plan: PatchPlanningOutput,
): PatchPlanValidationResult {
  const errors = [
    ...validateRationale(plan.rationale),
    ...validatePatchList(plan.patches),
  ];

  if (errors.length) {
    return {
      ok: false,
      errors,
    };
  }

  try {
    const simulatedResult = applyPatches(envelope, plan.patches);

    return {
      ok: true,
      errors: [],
      simulatedResult,
    };
  } catch (error) {
    const message =
      error instanceof PatchApplicationError
        ? error.message
        : "Patch 计划试运行时发生了未知错误。";

    return {
      ok: false,
      errors: [message],
    };
  }
}
