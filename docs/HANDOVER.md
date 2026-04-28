# 项目交接说明

## 1. 项目定位

`agent-ui-vue` 不是传统的“页面组件直接维护业务状态”的前端项目，而是一套 `Agent-driven UI Runtime Engine` 的前端原型。

核心链路是：

`用户交互 -> WorkflowEvent -> Runtime -> Patch Planner Agent -> PatchOperation[] -> applyPatches() -> UI 更新`

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
- 审批列表 `data_table` 示例
- 审核清单 `checklist` 示例
- 运行时支持“新增审核事项”
- 点击“批准”后生成审核报告 section

## 3. 关键目录与职责

### 核心协议

- [src/types/workflow.ts](C:/Users/PC/Documents/Codex/2026-04-24/github/agent-ui-vue/src/types/workflow.ts)

定义整个运行时的核心数据协议：

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
- 调用 Patch Planner
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

- 把用户事件解释成工作流迁移
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

这里定义了当前 demo 页面。

如果要快速调整 mock 展示效果，通常从这里入手。

## 4. 重要开发约束

维护这个项目时，请尽量遵守这些规则：

1. 不要在 widget 或页面组件里直接修改 `envelope`
2. 所有 UI 更新都优先设计成 `PatchOperation`
3. 新交互先定义 `WorkflowEvent`
4. 新 UI 类型先定义 schema，再补 widget 和 registry
5. 新 section 的变化优先使用 `replace_section / append_section / remove_section`
6. 不要把业务逻辑重新塞回 `App.vue` 或 widget

## 5. 当前 mock 交互说明

### 审批列表

在 `data_table` 示例中：

- 可以查看更接近真实业务的审批字段
- `查看详情` 会触发 `open_detail`
- 当前实现会在消息面板中返回一条提示消息

### 审核清单

在 `sec_main_review` 中：

- 勾选 checklist 会触发 `toggle_check`
- 新增审核事项输入框会触发 `add_checklist_item`
- runtime 会生成 patch 并回写 checklist

### 批准

点击“批准”后：

- `state` 变为 `presenting_result`
- 生成 `sec_review_report`
- 审核报告会插入到 `sec_main_review` 前面
- `allowedEvents` 被清空

### 退回修改

点击“退回修改”后：

- `state` 变为 `awaiting_revision`
- `sec_main_review` 被替换为结果区

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

1. checklist 勾选是否正常
2. 新增审核事项是否能回写 checklist
3. `data_table` 的“查看详情”是否会产生消息
4. 点击“批准”后是否生成审核报告 section
5. 点击“退回修改”后是否切到结果区

## 8. 已知情况

- 当前项目仍以 mock planner 为主，尚未接真实 Agent API
- 有过历史中文编码污染，新增或重写文件时建议统一使用 UTF-8
- 当前测试体系还不完整，更多依赖手测和 build 验证

## 9. 推荐后续方向

建议优先做这些事情：

1. 为 `patch.ts` 和 planner 补单元测试
2. 接入真实的 `PatchPlannerModel`
3. 把审核报告从单一 `text` 组件拆成结构化组件组合
4. 补充更多可插拔 widget
5. 增加更清晰的开发约束文档

## 10. 新同事接手建议

建议交接方式：

1. 先阅读 [README.md](C:/Users/PC/Documents/Codex/2026-04-24/github/agent-ui-vue/README.md) 与 [docs/Agent.md](C:/Users/PC/Documents/Codex/2026-04-24/github/agent-ui-vue/docs/Agent.md)
2. 结合本文件快速理解项目边界
3. 跑起本地页面并手测一遍
4. 从一个小任务开始熟悉，例如新增一个 widget 或新增一个 patch 行为

