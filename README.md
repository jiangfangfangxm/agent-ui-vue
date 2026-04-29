# agent-ui-vue

一个基于 `Vue 3 + Element Plus + TypeScript` 的 **Agent 驱动 UI Runtime Engine** 示例项目。

当前仓库的主示例已经演进为 **预警核查工作台**。它不是传统的“前端页面自己维护业务状态”，而是把界面演化拆成一条明确的运行链路：

```text
页面初始化 / 用户交互
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
- 页面动作先变成 `WorkflowEvent`
- Agent / Planner 根据上下文生成 `PatchOperation[]`
- Runtime 统一应用 patch
- Vue 根据新的 `WorkflowEnvelope` 自动重渲染

## 项目目标

构建一套可扩展的 Agent-driven UI Runtime，用于支持如下流程：

```text
Agent -> UI Schema -> Renderer -> UI -> User Interaction -> Event -> Agent -> Patch -> UI Update
```

当前示例聚焦在“预警核查”场景，包括：

- 页面启动时自动触发初始化事件
- 服务端通过 patch 回填预警详情
- 下发后台建议的核查方向
- 支持人工补充核查方向
- 执行核查后生成核查报告

## 当前示例能力

当前仓库已经支持：

- `WorkflowEnvelope` 驱动整页渲染
- Page / Section / Component 分层 renderer
- registry 驱动 widget 映射
- `useWorkflowRuntime()` 统一承接事件与状态流转
- `PatchOperation[]` 驱动 UI 增量更新
- `MockPatchPlannerModel` 模拟服务端 / Agent 生成 patch
- Python 版 patch builder，便于 Agent 调用与测试

## 动态 allowedEvents 生命周期

当前项目已经改成“**最小启动事件 + 初始化后动态下发真实事件**”的模式。

### 启动前

[src/mock/initialEnvelope.ts](C:/Users/PC/Documents/Codex/2026-04-24/github/agent-ui-vue/src/mock/initialEnvelope.ts) 里只保留：

```ts
allowedEvents: ["init_event"]
```

这意味着页面刚启动时，前端只允许触发初始化事件，避免在真实数据尚未回填前误触发业务交互。

### 初始化中

[src/App.vue](C:/Users/PC/Documents/Codex/2026-04-24/github/agent-ui-vue/src/App.vue) 挂载后会自动触发：

```text
init_event
```

`useWorkflowRuntime()` 会把它交给 planner，再由 planner 返回初始化 patch。

### 初始化完成后

[src/agent/MockPatchPlannerModel.ts](C:/Users/PC/Documents/Codex/2026-04-24/github/agent-ui-vue/src/agent/MockPatchPlannerModel.ts) 和 Python 端 [python/agent_patch_builders/workflow_action_builders.py](C:/Users/PC/Documents/Codex/2026-04-24/github/agent-ui-vue/python/agent_patch_builders/workflow_action_builders.py) 都会在 `init_event` 的 patch 里下发真正可用的事件：

- `toggle_check`
- `add_checklist_item`
- `Risk_Check_Event`
- `open_detail`

对应 patch 语义是：

```text
set_allowed_events([...真实可用事件...])
```

### 后续阶段

后续事件仍可继续通过 patch 调整 `allowedEvents`。例如执行核查完成后，当前 mock 会把事件白名单收紧为空，表示本轮核查已结束。

这套设计的价值在于：

- 启动阶段更安全
- 交互权限更贴近工作流状态
- 未来接真实后端时，可以由服务端统一控制当前可用动作

## 技术栈

- Vue 3
- TypeScript
- Element Plus
- Vite
- Python patch builders

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

### 4. Python patch-builder 测试

```bash
python -m unittest discover -s python/tests -p "test_*.py"
```

## 本地联调 Python patch 服务

当前前端已经接入本地 HTTP 版 Python patch 服务，用于让 `init_event`、`add_checklist_item`、`Risk_Check_Event` 等事件真正走 Python patch-builder。

### 联调结构

```text
浏览器
-> Vite 前端 (5173)
-> /api/patch-plan
-> Vite 代理
-> Python patch service (8000)
-> agent_patch_builders
-> 返回 PatchPlanningOutput
-> 前端 applyPatches()
```

### 当前配置

- 前端 planner 实现：
  - [src/agent/HttpPatchPlannerModel.ts](C:/Users/PC/Documents/Codex/2026-04-24/github/agent-ui-vue/src/agent/HttpPatchPlannerModel.ts)
- 前端运行时接线：
  - [src/composables/useWorkflowRuntime.ts](C:/Users/PC/Documents/Codex/2026-04-24/github/agent-ui-vue/src/composables/useWorkflowRuntime.ts)
- Vite 代理配置：
  - [vite.config.ts](C:/Users/PC/Documents/Codex/2026-04-24/github/agent-ui-vue/vite.config.ts)
- Python 本地服务入口：
  - [python/patch_service.py](C:/Users/PC/Documents/Codex/2026-04-24/github/agent-ui-vue/python/patch_service.py)

### 启动方式

需要同时启动两个进程。

终端 1：启动前端

```powershell
cd C:\Users\PC\Documents\Codex\2026-04-24\github\agent-ui-vue
npm run dev
```

终端 2：启动 Python patch 服务

```powershell
cd C:\Users\PC\Documents\Codex\2026-04-24\github\agent-ui-vue\python
python patch_service.py
```

### 健康检查

可以单独验证 Python 服务是否已经启动：

```powershell
curl http://127.0.0.1:8000/health
```

如果正常，会返回服务状态信息。

### 联调说明

- 页面加载后会自动触发 `init_event`
- `init_event` 会通过 `/api/patch-plan` 打到 Python 服务
- Python 服务会调用 `build_init_event_patches(...)`
- 返回的 patch 会继续由前端 `applyPatches()` 应用到页面

后续这些事件也会走同一条链路：

- `toggle_check`
- `add_checklist_item`
- `Risk_Check_Event`
- `open_detail`

### 常见问题

#### 1. 只启动了 Vite，没有启动 Python 服务

这时页面上的初始化或交互事件会请求失败，因为 `/api/patch-plan` 没有后端响应。

#### 2. Python 服务端口不是 8000

如果你修改了 Python 服务端口，需要同步修改 [vite.config.ts](C:/Users/PC/Documents/Codex/2026-04-24/github/agent-ui-vue/vite.config.ts) 里的代理目标地址。

#### 3. 想直接调用 Python patch-builder 做离线验证

可以继续使用：

```powershell
python -m unittest discover -s python/tests -p "test_*.py"
```

这适合验证 patch-builder 函数本身，不依赖前端页面。

## 当前页面结构

当前 mock 页面主要由这些 section 组成：

### 1. 预警情况详情

- 只有一个 `key_value` widget
- 初始时只显示占位内容
- 页面启动后自动触发 `init_event`
- 服务端返回 patch 后，回填真实预警详情

### 2. 关联台账

- 使用 `data_table` 展示与预警相关的关联案件 / 台账信息
- 支持状态列、金额列、时间列、链接列、操作列
- “查看详情”会触发 `open_detail`

### 3. 核查方向

- 使用 `checklist` 展示后台返回的核查建议
- 支持人工新增核查方向
- “新增核查方向”通过 patch 回写 checklist
- 主按钮为“执行核查”
- 点击后触发 `Risk_Check_Event`

### 4. 核查报告

- 由 `Risk_Check_Event` 返回 patch 动态生成
- 当前使用一个 `text` widget 展示核查报告正文

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

python/
  agent_patch_builders/
  tests/

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

### 页面初始化

- 页面挂载后自动触发 `init_event`
- planner 返回 patch
- 回填“预警情况详情”
- 回填“核查方向”
- 通过 `set_allowed_events` 开放真正可用的交互事件

### 核查方向勾选

- 勾选 checklist 触发 `toggle_check`
- Runtime 应用 patch 回写 checklist

### 新增核查方向

- 输入文本后触发 `add_checklist_item`
- Runtime 通过 patch 把新的核查方向回写到 checklist

### 执行核查

- 点击“执行核查”触发 `Risk_Check_Event`
- 服务端返回 patch
- 在报告 section 的 `text` 控件中显示核查结果

## 为什么这个架构重要

相对传统前端直接写业务状态判断，这个项目的优势在于：

- 前端组件不直接做业务状态迁移
- Agent / Planner 可以基于上下文和事件生成 UI patch
- UI 更新是增量的，而不是整页重建
- Runtime、Renderer、Widget、Patch Engine 分层清晰
- 后续接真实后端 / Python Agent 更自然

## 后续扩展方向

适合继续做的方向包括：

- 接入真实 `PatchPlannerModel`
- 为 `applyPatches()` 和 planner 增加测试
- 把核查报告从单一 `text` 组件拆成更结构化的 section
- 支持更多 schema / widget 类型
- 增加回放、审计和追踪能力

## 相关文档

- Agent 设计说明：[docs/Agent.md](C:/Users/PC/Documents/Codex/2026-04-24/github/agent-ui-vue/docs/Agent.md)
- 项目交接说明：[HANDOVER.md](C:/Users/PC/Documents/Codex/2026-04-24/github/agent-ui-vue/HANDOVER.md)
- Skill 规范：[docs/skills/workflow-patch-generation/SKILL.md](C:/Users/PC/Documents/Codex/2026-04-24/github/agent-ui-vue/docs/skills/workflow-patch-generation/SKILL.md)
