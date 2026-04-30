# agent-ui-vue

一个基于 `Vue 3 + Element Plus + TypeScript + Python` 的 **Agent 驱动 UI Runtime Engine** 示例项目。

当前主场景是 **预警核查工作台**。项目不是传统的“前端组件自己维护业务状态”，而是把界面演化拆成一条清晰链路：

```text
页面初始化 / 用户交互
-> WorkflowEvent
-> Runtime
-> Patch Planner
-> PatchOperation[]
-> applyPatches()
-> WorkflowEnvelope
-> Renderer
-> UI 更新
```

也就是说：

- UI 由 Schema 驱动
- 用户动作先变成 `WorkflowEvent`
- Agent / Planner 负责生成 `PatchOperation[]`
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
- 进入风险认定
- 有风险时进入行动计划
- 无风险时执行解警

## 当前能力

当前仓库已经支持：

- `WorkflowEnvelope` 驱动整页渲染
- Page / Section / Component 分层 renderer
- registry 驱动 widget 映射
- `useWorkflowRuntime()` 统一承接事件与状态流转
- `PatchOperation[]` 驱动 UI 增量更新
- Python 本地 patch 服务
- Python patch-builders，便于 Agent 调用与测试
- 动态 `allowedEvents` 生命周期控制

## 动态 allowedEvents 生命周期

当前项目已经改成“**最小启动事件 + 初始化后动态下发真实事件**”的模式。

### 启动前

[src/mock/initialEnvelope.ts](C:/Users/PC/Documents/Codex/2026-04-24/github/agent-ui-vue/src/mock/initialEnvelope.ts) 里只保留：

```ts
allowedEvents: ["init_event"]
```

含义是页面刚启动时，前端只允许执行初始化，不允许提前触发业务交互。

### 初始化中

[src/App.vue](C:/Users/PC/Documents/Codex/2026-04-24/github/agent-ui-vue/src/App.vue) 挂载后会自动触发 `init_event`。

### 初始化完成后

初始化 patch 会通过 `set_allowed_events` 下发真正可用的事件：

- `toggle_check`
- `add_checklist_item`
- `Risk_Check_Event`
- `open_detail`

### 报告阶段

执行核查后，`allowedEvents` 会切换为：

- `edit_report`
- `add_review_direction_after_report`
- `enter_risk_identification`
- `open_detail`

### 风险认定阶段

进入风险认定后，`allowedEvents` 会切换为：

- `set_risk_decision`
- `update_risk_reason`
- `resolve_no_risk`
- `confirm_risk_identification`
- `open_detail`

### 行动计划阶段

确认“有风险”后，`allowedEvents` 会切换为：

- `toggle_action_item`
- `add_action_item`
- `confirm_action_plan`
- `open_detail`

### 任务完成后

任务完成后会收紧为：

- `open_detail`

这样做的价值是：

- 启动阶段更安全
- 每个阶段允许的动作更明确
- 后续接真实后端时，可由服务端统一控制交互权限

## 技术栈

- Vue 3
- TypeScript
- Element Plus
- Vite
- Python

## 快速开始

### 1. 安装依赖

```bash
npm install
```

### 2. 启动前端

```bash
npm run dev
```

打开：

[http://localhost:5173/](http://localhost:5173/)

### 3. 前端构建

```bash
npm run build
```

### 4. Python 测试

```bash
python -m unittest discover -s python/tests -p "test_*.py"
```

## 本地联调 Python patch 服务

当前前端已经接入本地 HTTP Python patch 服务，用于让 `init_event`、`Risk_Check_Event`、`add_checklist_item` 等事件真正走 Python patch-builder。

### 联调结构

```text
浏览器 -> Vite 前端 (5173)
-> /api/patch-plan
-> Vite 代理
-> Python patch service (8000)
-> agent_patch_builders
-> 返回 PatchPlanningOutput
-> 前端 applyPatches()
```

### 相关文件

- 前端 planner：
  [src/agent/HttpPatchPlannerModel.ts](C:/Users/PC/Documents/Codex/2026-04-24/github/agent-ui-vue/src/agent/HttpPatchPlannerModel.ts)
- 前端运行时接线：
  [src/composables/useWorkflowRuntime.ts](C:/Users/PC/Documents/Codex/2026-04-24/github/agent-ui-vue/src/composables/useWorkflowRuntime.ts)
- Vite 代理配置：
  [vite.config.ts](C:/Users/PC/Documents/Codex/2026-04-24/github/agent-ui-vue/vite.config.ts)
- Python 服务入口：
  [python/patch_service.py](C:/Users/PC/Documents/Codex/2026-04-24/github/agent-ui-vue/python/patch_service.py)

### 启动方式

需要同时启动两个进程。

终端 1：前端

```powershell
cd C:\Users\PC\Documents\Codex\2026-04-24\github\agent-ui-vue
npm run dev
```

终端 2：Python patch 服务

```powershell
cd C:\Users\PC\Documents\Codex\2026-04-24\github\agent-ui-vue\python
python patch_service.py
```

### 健康检查

```powershell
curl http://127.0.0.1:8000/health
```

### 日志调试

Python patch 服务默认输出 `INFO` 级别日志，包含：

- 收到的事件类型
- 事件 id
- 当前 workflow state
- 当前 allowedEvents
- 生成了多少个 patch

如果你想看更详细日志，可在启动前设置：

```powershell
cd C:\Users\PC\Documents\Codex\2026-04-24\github\agent-ui-vue\python
$env:PATCH_SERVICE_LOG_LEVEL="DEBUG"
python patch_service.py
```

`DEBUG` 模式会额外输出：

- 初始化回填条目数量
- 风险核查报告长度
- 请求体解析成功提示
- builder 分支细节

恢复默认：

```powershell
$env:PATCH_SERVICE_LOG_LEVEL="INFO"
```

## 当前页面结构

当前 mock 页面主要由这些 section 组成：

### 1. 预警情况详情

- 标题：`预警情况详情`
- 只包含一个 `key_value` widget
- 启动时先显示占位内容
- `init_event` 后通过 patch 回填真实详情

### 2. 关联台账

- 使用 `data_table`
- 展示与预警相关的台账、案件或交易信息
- “查看详情”触发 `open_detail`

### 3. 核查方向

- 使用 `checklist`
- 显示服务端返回的核查建议
- 支持人工新增核查方向
- 主按钮为“执行核查”
- 点击后触发 `Risk_Check_Event`

### 4. 核查报告

- 由 `Risk_Check_Event` 返回 patch 动态生成
- 使用 `text` widget 展示报告内容

### 5. 报告后续处理

执行核查后新增 `sec_report_actions`，包含 3 个按钮：

- 修改核查报告
- 新增核查方向
- 进入风险认定环节

### 6. 风险认定

进入风险认定后新增 `sec_risk_identification`，包含：

- 有风险 / 无风险
- 风险认定说明
- 后续确认按钮

### 7. 行动计划

当用户确认“有风险”后，新增 `sec_action_plan`，包含：

- 推荐行动 checklist
- 新增行动事项输入框
- 确认行动计划按钮

### 8. 处置结果

- 无风险：生成 `sec_resolution_result_no_risk`
- 有风险并确认行动计划：生成 `sec_resolution_result_with_action`

## 当前工作流

### 路径 1：无风险闭环

```text
init_event
-> 回填预警详情与核查方向
-> 执行核查
-> 生成核查报告
-> 进入风险认定
-> 选择“无风险”
-> 填写风险认定说明
-> 确认无风险并解警
-> 任务完成
```

### 路径 2：有风险 + 行动计划闭环

```text
init_event
-> 回填预警详情与核查方向
-> 执行核查
-> 生成核查报告
-> 进入风险认定
-> 选择“有风险”
-> 填写风险认定说明
-> 确认有风险
-> 进入行动计划
-> 勾选 / 新增行动事项
-> 确认行动计划
-> 任务完成
```

## 目录结构

```text
src/
  App.vue
  main.ts

  agent/
  types/
  composables/
  utils/
  mock/

  components/
    layout/
    renderer/
    widgets/

python/
  agent_patch_builders/
  tests/
  patch_service.py

docs/
  Agent.md
  skills/
```

## 核心概念

### WorkflowEnvelope

`WorkflowEnvelope` 是当前 UI 状态的唯一真相，包含：

- 当前工作流状态
- 当前页面 schema
- 消息列表
- 风险摘要
- 当前允许事件

### PatchOperation

当前支持：

- `set_state`
- `replace_section`
- `append_section`
- `remove_section`
- `prepend_message`
- `set_allowed_events`
- `set_risk_summary`

其中 `append_section` 支持 `beforeSectionId`，可用于把 section 插入到指定位置之前。

### useWorkflowRuntime

`useWorkflowRuntime()` 负责：

- 持有 `WorkflowEnvelope`
- 接收 `WorkflowEvent`
- 调用 planner
- 校验 patch 计划
- 应用 patch
- 更新界面

### Python patch-builders

[python/agent_patch_builders](C:/Users/PC/Documents/Codex/2026-04-24/github/agent-ui-vue/python/agent_patch_builders) 负责：

- 在 Python 环境中生成 patch
- 作为本地 HTTP patch 服务的业务核心
- 为后续真实 Agent 接入提供可测试的 patch 生成层

## 建议手测路径

每次改动后建议至少验证：

1. 页面加载后是否自动触发 `init_event`
2. “预警情况详情”是否被正确回填
3. “核查方向”是否显示后台建议
4. 新增核查方向后 checklist 是否回写
5. 点击“执行核查”后是否出现：
   - `sec_review_report`
   - `sec_report_actions`
6. 进入风险认定后：
   - “无风险”路径是否能解警
   - “有风险”路径是否能进入行动计划
7. 行动计划中：
   - 勾选推荐行动是否回写
   - 新增行动事项是否回写
   - 确认行动计划后是否任务完成

## 后续扩展方向

- 接入真实 `PatchPlannerModel`
- 把核查报告从单一 `text` 组件拆成结构化 section
- 给风险认定与行动计划增加更专业的表单 widget
- 补充更多单元测试与联调测试
- 引入操作审计与事件回放能力

## 相关文档

- Agent 设计说明：[docs/Agent.md](C:/Users/PC/Documents/Codex/2026-04-24/github/agent-ui-vue/docs/Agent.md)
- 项目交接说明：[HANDOVER.md](C:/Users/PC/Documents/Codex/2026-04-24/github/agent-ui-vue/HANDOVER.md)
- Skill 规范：[docs/skills/workflow-patch-generation/SKILL.md](C:/Users/PC/Documents/Codex/2026-04-24/github/agent-ui-vue/docs/skills/workflow-patch-generation/SKILL.md)
