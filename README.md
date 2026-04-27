# agent-ui-vue

一个基于 `Vue 3 + Element Plus + TypeScript` 的 **Agent 驱动 UI Runtime Engine** 示例项目。

这个项目不是传统的“前端自己维护页面状态”的方式，而是把界面演化拆成一条清晰链路：

```text
Agent / Planner
-> PatchOperation[]
-> applyPatches()
-> WorkflowEnvelope
-> Renderer
-> UI
```

也就是说：

- UI 由 JSON Schema 驱动
- 用户交互会变成 `WorkflowEvent`
- Agent 或 Patch Planner 根据上下文生成 `PatchOperation[]`
- Runtime 统一应用 patch
- Vue 根据新的 `WorkflowEnvelope` 自动重新渲染页面

## 项目目标

构建一个“智能体驱动界面”的运行时引擎，用于支持如下流程：

```text
Agent -> UI Schema -> Renderer -> UI -> User Interaction -> Event -> Agent -> Patch -> UI Update
```

## 当前能力

当前项目已经具备这些能力：

- 基于 `WorkflowEnvelope` 渲染页面
- 支持多种 widget 类型
- 使用 registry 驱动组件映射
- 使用 `useWorkflowRuntime()` 承接事件与状态更新
- 通过 `PatchOperation[]` 更新 UI，而不是整页重建
- 提供一个 `MockPatchPlannerModel` 模拟 Agent 生成 patch
- 提供 Patch Planner Agent 协议与校验层

## 技术栈

- Vue 3
- TypeScript
- Element Plus
- Vite

## 快速开始

### 1. 安装依赖

```bash
npm install
```

### 2. 启动开发环境

```bash
npm run dev
```

启动后打开：

[http://localhost:5173/](http://localhost:5173/)

### 3. 构建生产版本

```bash
npm run build
```

## 目录结构

```text
src/
  App.vue
  main.ts

  agent/
    contracts.ts
    PatchPlannerAgent.ts
    MockPatchPlannerModel.ts
    validatePatchPlan.ts

  types/
    workflow.ts

  composables/
    useWorkflowRuntime.ts

  utils/
    patch.ts
    labelMappers.ts

  mock/
    initialEnvelope.ts
    mockPatchEngine.ts

  components/
    layout/
    renderer/
    widgets/

docs/
  Agent.md
  skills/
    workflow-patch-generation/
```

## 核心概念

### 1. WorkflowEnvelope

`WorkflowEnvelope` 是当前 UI 状态的唯一真相，包含：

- 当前工作流状态
- 当前页面 schema
- 消息列表
- 风险摘要
- 当前允许触发的事件

### 2. PatchOperation

Patch 是 UI 更新的最小操作单元。当前支持：

- `set_state`
- `replace_section`
- `append_section`
- `remove_section`
- `prepend_message`
- `set_allowed_events`
- `set_risk_summary`

### 3. useWorkflowRuntime

`useWorkflowRuntime()` 是运行时核心，负责：

- 持有 `WorkflowEnvelope`
- 接收 `WorkflowEvent`
- 调用 Patch Planner Agent
- 校验 patch 计划
- 应用 patch
- 更新界面

### 4. Patch Planner Agent

Patch Planner Agent 的职责不是直接渲染界面，而是：

1. 读取当前 `WorkflowEnvelope`
2. 理解用户动作
3. 规划工作流迁移
4. 输出最小、合法的 patch 集

详细说明见：

- [docs/Agent.md](C:/Users/PC/Documents/Codex/2026-04-24/github/agent-ui-vue/docs/Agent.md)

## 当前示例交互

项目中内置了一个审核工作台示例，支持：

- 勾选审核清单
- 点击“批准”
- 点击“退回修改”
- 触发消息更新
- 触发风险摘要更新
- 将主审核区替换为结果区

## 为什么这个架构重要

相对于传统前端直接写业务状态判断，这个项目的优势在于：

- 前端组件不直接做业务状态迁移
- Agent 可以基于上下文和用户动作生成 UI patch
- UI 更新是增量的，而不是整页重建
- Runtime、Renderer、Widget、Patch Engine 分层清晰
- 后续接真实模型或后端 Agent 更自然

## 后续扩展方向

适合继续做的方向包括：

- 接入真实 `OpenAIPatchPlannerModel`
- 增加强规则 patch 校验
- 增加测试覆盖 `applyPatches()` 与 planner
- 支持 WebSocket 流式 patch 更新
- 支持更多 schema / widget 类型
- 增加审计、回放与追踪能力

## 相关文档

- Agent 设计说明：[docs/Agent.md](C:/Users/PC/Documents/Codex/2026-04-24/github/agent-ui-vue/docs/Agent.md)
- Skill 规范：[docs/skills/workflow-patch-generation/SKILL.md](C:/Users/PC/Documents/Codex/2026-04-24/github/agent-ui-vue/docs/skills/workflow-patch-generation/SKILL.md)
