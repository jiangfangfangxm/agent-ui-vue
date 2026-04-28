# agent-ui-vue

一个基于 `Vue 3 + Element Plus + TypeScript` 的 **Agent 驱动 UI Runtime Engine** 示例项目。

当前仓库里的主示例已经演进为 **预警核查工作台**。它不是传统的“前端页面自己维护业务状态”的实现方式，而是把界面演化拆成一条明确的运行链路：

```text
用户交互 / 页面初始化
-> WorkflowEvent
-> Runtime
-> Patch Planner Agent
-> PatchOperation[]
-> applyPatches()
-> WorkflowEnvelope
-> Renderer
-> UI 更新
```

也就是说：

- UI 由 Schema 驱动
- 用户动作先变成 `WorkflowEvent`
- Agent / Planner 根据上下文生成 `PatchOperation[]`
- Runtime 统一应用 patch
- Vue 根据新的 `WorkflowEnvelope` 自动重渲染

## 项目目标

构建一套可扩展的 Agent-driven UI Runtime，用于支持这类流程：

```text
Agent -> UI Schema -> Renderer -> UI -> User Interaction -> Event -> Agent -> Patch -> UI Update
```

当前示例聚焦在“预警核查”场景，包括：

- 页面启动时自动触发初始化事件
- 服务端返回 patch 回填预警详情
- 展示后台建议的核查方向
- 支持人工补充核查方向
- 执行风险核查后生成报告区

## 当前示例能力

当前仓库已经支持：

- `WorkflowEnvelope` 驱动整页渲染
- Page / Section / Component 分层 renderer
- registry 驱动 widget 映射
- `useWorkflowRuntime()` 统一承接事件和状态流转
- `PatchOperation[]` 驱动 UI 增量更新
- `MockPatchPlannerModel` 模拟服务端 / Agent 生成 patch
- 页面启动自动触发 `init_event`
- “执行核查”触发 `Risk_Check_Event` 并生成核查报告

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

### 3. 构建

```bash
npm run build
```

## 当前页面结构

当前 mock 页面主要由这些 section 组成：

### 1. 预警情况详情

- 只有一个 `key_value` widget
- 页面初始时先显示占位值
- `App.vue` 挂载后自动触发 `init_event`
- `MockPatchPlannerModel` 模拟服务端返回 patch
- patch 会更新该 section 的 KV 内容

### 2. 关联台账

- 使用 `data_table` 展示与预警相关的关联案件 / 台账信息
- 支持状态列、金额列、操作列
- “查看详情”会触发 `open_detail`

### 3. 核查方向

- 使用 `checklist` 展示后台返回的核查建议
- 支持手动新增核查方向
- “新增核查方向”仍然通过 patch 回写 checklist
- 主按钮为“执行核查”
- 点击后触发 `Risk_Check_Event`

### 4. 核查报告

- 由 `Risk_Check_Event` 返回 patch 生成
- 当前用一个 `text` widget` 展示核查报告正文

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

### WorkflowEnvelope

`WorkflowEnvelope` 是当前 UI 状态的唯一真相，包含：

- 当前工作流状态
- 当前页面 schema
- 消息列表
- 风险摘要
- 当前允许触发的事件

### PatchOperation

Patch 是 UI 更新的最小操作单元。当前支持：

- `set_state`
- `replace_section`
- `append_section`
- `remove_section`
- `prepend_message`
- `set_allowed_events`
- `set_risk_summary`

其中 `append_section` 还支持 `beforeSectionId`，可用于把新 section 插入到指定位置前面。

### useWorkflowRuntime

`useWorkflowRuntime()` 是运行时核心，负责：

- 持有 `WorkflowEnvelope`
- 接收 `WorkflowEvent`
- 调用 Patch Planner Agent
- 校验 patch 计划
- 应用 patch
- 更新界面

### Patch Planner Agent

Patch Planner Agent 不直接渲染界面，而是：

1. 读取当前 `WorkflowEnvelope`
2. 理解初始化事件或用户动作
3. 规划工作流迁移
4. 输出最小、合法的 patch 集

详细说明见：

- [docs/Agent.md](C:/Users/PC/Documents/Codex/2026-04-24/github/agent-ui-vue/docs/Agent.md)

## 当前示例交互

当前预警核查工作台中，主要交互包括：

### 页面初始化

- 页面挂载后自动触发 `init_event`
- 服务端 mock 返回 patch
- 更新“预警情况详情”
- 更新“核查方向”

### 核查方向勾选

- 勾选 checklist 触发 `toggle_check`
- Runtime 应用 patch 回写 checklist

### 新增核查方向

- 输入文本后触发 `add_checklist_item`
- Runtime 通过 patch 把新的核查方向回写到 checklist

### 执行核查

- 点击“执行核查”触发 `Risk_Check_Event`
- 服务端 mock 返回 patch
- 在报告 section 的 `text` 控件中显示核查结果

## 为什么这个架构重要

相对于传统前端直接写业务状态判断，这个项目的优势在于：

- 前端组件不直接做业务状态迁移
- Agent / Planner 可以基于上下文和事件生成 UI patch
- UI 更新是增量的，而不是整页重建
- Runtime、Renderer、Widget、Patch Engine 分层清晰
- 后续接真实后端 Agent 更自然

## 后续扩展方向

适合继续做的方向包括：

- 接入真实 `PatchPlannerModel`
- 为 `applyPatches()` 与 planner 增加测试
- 把核查报告从单一 `text` 组件拆成更结构化的 section
- 支持更多 schema / widget 类型
- 增加回放、审计和追踪能力

## 相关文档

- Agent 设计说明：[docs/Agent.md](C:/Users/PC/Documents/Codex/2026-04-24/github/agent-ui-vue/docs/Agent.md)
- 交接说明：[HANDOVER.md](C:/Users/PC/Documents/Codex/2026-04-24/github/agent-ui-vue/HANDOVER.md)
- Skill 规范：[docs/skills/workflow-patch-generation/SKILL.md](C:/Users/PC/Documents/Codex/2026-04-24/github/agent-ui-vue/docs/skills/workflow-patch-generation/SKILL.md)
