import type {
  PatchOperation,
  WorkflowEnvelope,
  WorkflowEvent,
} from "../types/workflow";

/**
 * Patch 规划时可注入的上下文。
 * 这些上下文不直接参与渲染，而是给 Agent 做决策参考。
 */
export interface PatchPlanningContext {
  businessContext?: Record<string, unknown>;
  policyContext?: Record<string, unknown>;
  sessionContext?: Record<string, unknown>;
}

/**
 * Patch Planner Agent 的标准输入。
 */
export interface PatchPlanningInput {
  envelope: WorkflowEnvelope;
  event: WorkflowEvent;
  context?: PatchPlanningContext;
}

/**
 * Patch Planner Agent 的标准输出。
 * patches 是真正驱动 UI 更新的结果；
 * rationale 用于解释为什么要这样迁移工作流；
 * warnings 用于补充风险或策略提醒。
 */
export interface PatchPlanningOutput {
  patches: PatchOperation[];
  rationale: string;
  warnings?: string[];
}

/**
 * Patch Planner Agent 对外暴露的最小接口。
 */
export interface PatchPlannerAgent {
  plan(input: PatchPlanningInput): Promise<PatchPlanningOutput>;
}
