import type {
  PatchPlannerAgent,
  PatchPlanningInput,
  PatchPlanningOutput,
} from "./contracts";
import { validatePatchPlan } from "./validatePatchPlan";

/**
 * 底层模型接口。
 * 后续可以替换成真实 LLM、后端 Agent 服务或规则引擎。
 */
export interface PatchPlannerModel {
  generate(input: PatchPlanningInput): Promise<PatchPlanningOutput>;
}

/**
 * 运行时使用的 Patch Planner Agent。
 * 它负责调用底层模型，并在结果进入前端前完成合法性校验。
 */
export class RuntimePatchPlannerAgent implements PatchPlannerAgent {
  constructor(private readonly model: PatchPlannerModel) {}

  async plan(input: PatchPlanningInput): Promise<PatchPlanningOutput> {
    const plan = await this.model.generate(input);
    const validation = validatePatchPlan(input.envelope, plan);

    if (!validation.ok) {
      throw new Error(
        `Patch 计划校验失败：${validation.errors.join(" | ")}`,
      );
    }

    return plan;
  }
}
