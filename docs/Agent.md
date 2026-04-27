# Patch Planner Agent 说明

## 1. 这个 Agent 是干什么的

本项目中的 Agent 不是通用聊天代理，而是一个专门负责“规划 UI Patch”的 Agent。

它的职责是：

1. 读取当前 `WorkflowEnvelope`
2. 理解用户触发的 `WorkflowEvent`
3. 结合业务上下文判断工作流应如何迁移
4. 输出最小、合法、可执行的 `PatchOperation[]`

它不直接渲染 UI，也不直接修改 Vue 组件局部状态。

## 2. 它在系统里的位置

运行链路如下：

```text
Widget 交互
-> dispatchEvent()
-> RuntimePatchPlannerAgent.plan()
-> PatchPlannerModel.generate()
-> validatePatchPlan()
-> applyPatches()
-> Vue 响应式重渲染
```

对应代码：

- runtime 入口: `src/composables/useWorkflowRuntime.ts`
- Agent 协议: `src/agent/contracts.ts`
- Agent 执行层: `src/agent/PatchPlannerAgent.ts`
- Mock 模型: `src/agent/MockPatchPlannerModel.ts`
- Patch 计划校验: `src/agent/validatePatchPlan.ts`

## 3. 角色分层

### 3.1 PatchPlannerModel

这是最底层的“产出 patch 计划”的模型接口：

```ts
interface PatchPlannerModel {
  generate(input: PatchPlanningInput): Promise<PatchPlanningOutput>;
}
```

当前实现是 `MockPatchPlannerModel`。  
后续可以替换为：

- OpenAI Responses API
- 后端 Agent 服务
- WebSocket 流式 Agent
- 规则引擎 + LLM 混合模型

### 3.2 RuntimePatchPlannerAgent

这是运行时真正调用的 Agent 执行层。

它负责：

- 调用底层模型
- 对模型返回的 patch 计划做结构和执行合法性校验
- 只把通过校验的结果交给 runtime

### 3.3 validatePatchPlan

这是安全闸门。

它负责：

- 检查是否存在 `patches`
- 检查是否存在 `rationale`
- 试运行 `applyPatches()`，确认当前 plan 能作用于当前 `envelope`

## 4. 输入输出协议

### 输入

```ts
interface PatchPlanningInput {
  envelope: WorkflowEnvelope;
  event: WorkflowEvent;
  context?: {
    businessContext?: Record<string, unknown>;
    policyContext?: Record<string, unknown>;
    sessionContext?: Record<string, unknown>;
  };
}
```

### 输出

```ts
interface PatchPlanningOutput {
  patches: PatchOperation[];
  rationale: string;
  warnings?: string[];
}
```

## 5. 设计原则

### 5.1 输出最小 patch 集

Agent 应优先输出最小 patch 集，而不是整页 UI 替换。

建议优先顺序：

1. `set_state`
2. `replace_section`
3. `prepend_message`
4. `set_allowed_events`
5. `set_risk_summary`
6. `append_section`
7. `remove_section`

### 5.2 先迁移状态，再更新界面

Agent 应先判断工作流状态如何迁移，再规划 UI patch。

不要从“页面应该长什么样”倒推业务状态。

### 5.3 所有输出都必须可验证

Agent 输出的 patch 必须能通过：

- `validatePatchPlan()`
- `applyPatches()`

否则不应进入前端状态流。

## 6. 当前 Mock 能力

当前 `MockPatchPlannerModel` 支持两个事件：

- `toggle_check`
- `submit_decision`

其中：

- `toggle_check` 会替换主审核区的 checklist section，并插入一条消息
- `submit_decision` 会迁移 workflow state，并把主审核区替换为结果区

## 7. 后续扩展建议

### 7.1 替换成真实模型

可以新增一个例如 `OpenAIPatchPlannerModel.ts`：

```ts
class OpenAIPatchPlannerModel implements PatchPlannerModel {
  async generate(input: PatchPlanningInput): Promise<PatchPlanningOutput> {
    // 调用真实模型
  }
}
```

然后在 runtime 中替换当前的 `MockPatchPlannerModel`。

### 7.2 增加强规则验证

未来可以在 `validatePatchPlan()` 中继续增加规则，例如：

- `set_state` 是否是合法状态迁移
- `replace_section` 是否只作用于允许区域
- `set_allowed_events` 是否包含未知事件
- `set_risk_summary` 是否缺少必要字段

### 7.3 增加审计记录

可以把 `PatchPlanningOutput.rationale` 和最终 patch 一起写入事件审计流，用于：

- 排查错误
- 回放会话
- 解释 Agent 决策

## 8. 与 Skill 的关系

项目内 Agent 是运行时代码实现。

`docs/skills/workflow-patch-generation/` 下的 Skill 是给另一个 Agent 或模型的“行为规范”。

可以这样理解：

- `Agent.md` 讲的是系统里的 Agent 怎么实现
- `SKILL.md` 讲的是模型在生成 patch 时应遵守什么规则
