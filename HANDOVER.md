# 项目交接说明

## 1. 项目定位

`agent-ui-vue` 不是传统的“页面组件直接维护业务状态”的前端项目，而是一套 `Agent-driven UI Runtime Engine` 的前端原型。

当前主示例场景已经演进为：

**预警核查工作台**

核心链路是：

`页面初始化 / 用户交互 -> WorkflowEvent -> Runtime -> Patch Planner Agent -> PatchOperation[] -> applyPatches() -> UI 更新`

这意味着：

- UI 由 JSON Schema 驱动渲染
- 前端组件不直接修改业务状态
- 所有 UI 更新都应通过 Patch Engine
- Agent / Planner 负责决定“页面该怎么变”

## 2. 当前已实现能力

- Vue3 + Element Plus 运行骨架
- Schema-driven renderer
- Widget registry
- Patch Engine
- Mock Patch Planner Agent
- 页面启动自动触发 `init_event`
- `init_event` 回填预警详情与核查方向
- 关联台账 `data_table` 示例
- 支持人工新增核查方向
- 点击“执行核查”触发 `Risk_Check_Event`
- 根据风险核查结果生成报告 section

## 3. 关键目录与职责

### 核心协议

- [src/types/workflow.ts](C:/Users/PC/Documents/Codex/2026-04-24/github/agent-ui-vue/src/types/workflow.ts)

这里定义运行时共享的数据模型：

- `WorkflowEnvelope`
- `UIPageSchema`
- `UISection`
- `UIComponent`
- `WorkflowEvent`
- `PatchOperation`

### Runtime 层

- [src/composables/useWorkflowRuntime.ts](C:/Users/PC/Documents/Codex/2026-04-24/github/agent-ui-vue/src/composables/useWorkflowRuntime.ts)

职责：

- 持有当前 `envelope`
- 记录 `eventLog`
- 接收 `dispatchEvent`
- 调用 planner
- 调用 `applyPatches()`
- 维护 runtime 状态和错误态

### Patch Engine

- [src/utils/patch.ts](C:/Users/PC/Documents/Codex/2026-04-24/github/agent-ui-vue/src/utils/patch.ts)

这是状态更新的唯一正式入口。  
所有 `WorkflowEnvelope` 更新都应通过这里完成。

### Agent / Planner

- [src/agent/PatchPlannerAgent.ts](C:/Users/PC/Documents/Codex/2026-04-24/github/agent-ui-vue/src/agent/PatchPlannerAgent.ts)
- [src/agent/MockPatchPlannerModel.ts](C:/Users/PC/Documents/Codex/2026-04-24/github/agent-ui-vue/src/agent/MockPatchPlannerModel.ts)
- [src/agent/contracts.ts](C:/Users/PC/Documents/Codex/2026-04-24/github/agent-ui-vue/src/agent/contracts.ts)
- [src/agent/validatePatchPlan.ts](C:/Users/PC/Documents/Codex/2026-04-24/github/agent-ui-vue/src/agent/validatePatchPlan.ts)

职责：

- 把事件解释成工作流迁移
- 生成 `PatchOperation[]`
- 校验 patch 计划是否合法

当前是 mock 实现，后面可以替换为真实模型。

### Renderer 层

- [src/components/renderer/PageRenderer.vue](C:/Users/PC/Documents/Codex/2026-04-24/github/agent-ui-vue/src/components/renderer/PageRenderer.vue)
- [src/components/renderer/SectionRenderer.vue](C:/Users/PC/Documents/Codex/2026-04-24/github/agent-ui-vue/src/components/renderer/SectionRenderer.vue)
- [src/components/renderer/ComponentRenderer.vue](C:/Users/PC/Documents/Codex/2026-04-24/github/agent-ui-vue/src/components/renderer/ComponentRenderer.vue)
- [src/components/renderer/registry.ts](C:/Users/PC/Documents/Codex/2026-04-24/github/agent-ui-vue/src/components/renderer/registry.ts)

职责：

- 把 Schema 解释成真实 Vue 组件树
- 根据 `type` 从 registry 找到对应 widget

### Widgets 层

- [src/components/widgets](C:/Users/PC/Documents/Codex/2026-04-24/github/agent-ui-vue/src/components/widgets)

职责：

- 显示具体 UI
- 采集用户输入
- 发出 `WorkflowEvent`

原则：

- widget 不直接改 `WorkflowEnvelope`
- widget 只做展示和事件发射

### Mock 页面入口

- [src/mock/initialEnvelope.ts](C:/Users/PC/Documents/Codex/2026-04-24/github/agent-ui-vue/src/mock/initialEnvelope.ts)

这里定义当前 demo 页面：

- 预警情况详情
- 关联台账
- 核查方向
- 审计面板

## 4. 当前 mock 交互说明

### 页面初始化

页面挂载后，`App.vue` 会自动触发：

- `init_event`

随后 mock planner 会返回 patch：

- 更新 `sec_overview`
- 更新 `sec_main_review`
- 移除 `init_event` 的允许权限
- 更新风险摘要
- 追加初始化消息

### 预警情况详情

`sec_overview` 里只有一个 `key_value` widget。

初始内容只是占位值，真正的预警详情来自 `init_event` 触发后的 patch 回填。

### 核查方向

`sec_main_review` 的标题已经改成：

- `核查方向`

其中 checklist 内容不再是前端写死的审核项，而是 mock 服务端返回的核查建议。

### 新增核查方向

输入框标题已经改成：

- `新增核查方向`

交互机制保持不变：

- 输入文本
- 触发 `add_checklist_item`
- planner 返回 patch
- checklist 被回写更新

### 执行核查

主按钮已改成：

- `执行核查`

触发事件：

- `Risk_Check_Event`

当前行为：

- planner 返回风险核查报告 patch
- 生成或更新 `sec_review_report`
- 报告内容通过 `text` widget 展示

### 关联台账

`data_table` 目前用于展示与预警相关的台账信息。  
“查看详情”会触发：

- `open_detail`

当前只在消息面板中返回提示消息。

## 5. 重要开发约束

维护这个项目时，请尽量遵守这些规则：

1. 不要在 widget 或页面组件里直接修改 `envelope`
2. 所有 UI 更新都优先设计成 `PatchOperation`
3. 新交互先定义 `WorkflowEvent`
4. 新 UI 类型先定义 schema，再补 widget 和 registry
5. 新 section 的变化优先使用 `replace_section / append_section / remove_section`
6. 不要把业务逻辑重新塞回 `App.vue` 或 widget

## 6. 开发与运行

### 安装依赖

```powershell
npm install
```

### 启动开发环境

```powershell
npm run dev
```

### 构建

```powershell
npm run build
```

## 7. 建议手测路径

每次改动后，至少验证：

1. 页面打开后是否自动触发 `init_event`
2. “预警情况详情”是否被自动回填
3. “核查方向”是否显示服务端建议
4. 新增核查方向是否能回写 checklist
5. “执行核查”后是否生成核查报告 section
6. `data_table` 的“查看详情”是否会产生消息

## 8. 已知情况

- 当前项目仍以 mock planner 为主，尚未接真实 Agent API
- 历史上有过中文编码污染，新增或重写文件时建议统一使用 UTF-8
- 当前测试体系还不完整，更多依赖手测和 build 验证

## 9. 推荐后续方向

建议优先做这些事情：

1. 为 `patch.ts` 和 planner 补单元测试
2. 接入真实的 `PatchPlannerModel`
3. 把核查报告从单一 `text` 组件拆成结构化组件组合
4. 把 `init_event` 替换成真实后端初始化接口
5. 增强事件审计与回放能力

## 10. 新同事接手建议

建议交接方式：

1. 先阅读 [README.md](C:/Users/PC/Documents/Codex/2026-04-24/github/agent-ui-vue/README.md) 与 [docs/Agent.md](C:/Users/PC/Documents/Codex/2026-04-24/github/agent-ui-vue/docs/Agent.md)
2. 结合本文件快速理解项目边界
3. 跑起本地页面并手测一遍
4. 从一个小任务开始熟悉，例如新增一个 widget 或新增一个 patch 行为
