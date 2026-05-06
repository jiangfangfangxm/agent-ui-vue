# AGENTS.md

## 项目定位

`agent-ui-vue` 是一个 **Agent-driven UI Runtime Engine** 示例项目，当前主应用是：

- **预警核查工作台**

它不是传统的“组件内部直接维护业务状态”的前端项目，而是把页面演化拆成一条稳定链路：

```text
页面初始化 / 用户操作
-> WorkflowEvent
-> useWorkflowRuntime()
-> Patch Planner
-> PatchOperation[]
-> applyPatches()
-> WorkflowEnvelope
-> Renderer
-> UI 更新
```

维护时请始终记住：

- UI 由 `WorkflowEnvelope` 和 schema 驱动
- 业务真实状态放在 `WorkflowContext`
- widget 只发事件，不直接改业务状态
- 所有状态和 UI 更新都应通过 `PatchOperation[]`
- `allowedEvents` 是阶段交互边界
- 前端和 Python patch service 都会校验事件契约

## 当前业务模式

当前主流程是三阶段应用：

```text
风险核查 -> 风险认定 -> 后续行动计划制定
```

主路径：

1. 页面启动后自动触发 `init_event`
2. Python patch service 回填预警详情和核查方向
3. 用户勾选或新增核查方向
4. 执行核查并生成核查报告
5. 报告阶段可修改报告、补充核查方向或进入风险认定
6. 风险认定选择无风险或有风险
7. 无风险路径：解警并完成任务
8. 有风险路径：进入行动计划，确认后完成任务

## 核心阶段

| 状态 | 含义 |
| --- | --- |
| `reviewing` | 风险核查阶段 |
| `report_reviewing` | 核查报告后续处理阶段 |
| `awaiting_revision` | 核查报告修改子流程 |
| `risk_identifying` | 风险认定阶段 |
| `action_planning` | 后续行动计划制定阶段 |
| `resolved_no_risk` | 无风险解警完成 |
| `resolved_with_action` | 有风险且行动计划确认完成 |
| `presenting_result` | 结果展示兼容状态，当前主路径较少直接使用 |

## 重要事件

初始化：

- `init_event`

核查阶段：

- `toggle_check`
- `add_checklist_item`
- `Risk_Check_Event`
- `open_detail`

报告阶段：

- `edit_report`
- `save_report_revision`
- `cancel_report_revision`
- `add_review_direction_after_report`
- `submit_new_direction_after_report`
- `cancel_add_direction`
- `enter_risk_identification`

风险认定阶段：

- `set_risk_decision`
- `update_risk_reason`
- `resolve_no_risk`
- `confirm_risk_identification`

行动计划阶段：

- `toggle_action_item`
- `add_action_item`
- `confirm_action_plan`

任务完成后通常只保留：

- `open_detail`

## 关键目录和文件

前端：

- `src/App.vue`
  - 页面入口
  - 自动触发 `init_event`
  - 右上角提供“运行台 / 配置工具”切换

- `src/composables/useWorkflowRuntime.ts`
  - Runtime 中枢
  - 持有 `WorkflowEnvelope`
  - 记录事件日志
  - 调用 planner
  - 应用 patch
  - 维护 runtime 状态和错误提示

- `src/types/workflow.ts`
  - 核心协议定义
  - 包含 `WorkflowEnvelope`、`WorkflowContext`、`WorkflowEvent`、`PatchOperation`、`WorkflowState`、`UISection`、`UIComponent`

- `src/workflow/definition.ts`
  - 前端事件契约入口
  - 优先读取 generated 配置
  - generated 不存在或缺项时回退到手写定义

- `src/workflow/appConfig.ts`
  - 加载 `generated/warning_review_workbench/app.normalized.json`
  - 提供 `createContextFromAppConfig()`、`getAllowedEventsFromAppConfig()`、`getEventConfig()`、`validatePayloadBySchema()`

- `src/utils/patch.ts`
  - 前端 Patch Engine
  - 唯一的前端状态变更入口
  - 已支持 `set_context`

- `src/agent/HttpPatchPlannerModel.ts`
  - 通过 `/api/patch-plan` 调用 Python patch service
  - 连接不上 `127.0.0.1:8000` 时会给出明确错误提示

- `src/components/renderer/`
  - schema 渲染层
  - 包含 `PageRenderer.vue`、`SectionRenderer.vue`、`ComponentRenderer.vue`、`registry.ts`

- `src/components/widgets/`
  - 具体 widget 实现
  - 包含 `ChecklistWidget.vue`、`ButtonGroupWidget.vue`、`TextInputWidget.vue`、`KeyValueWidget.vue`、`DataTableWidget.vue`

- `src/components/config/BusinessConfigTool.vue`
  - 第一版业务配置工具
  - 支持编辑应用、阶段、事件、区块
  - 支持基础引用校验
  - 支持导出 YAML
  - 支持“编译”页展示检查、CLI 命令和预计产物
  - 当前只在浏览器内存中编辑，不直接写文件或执行 Python

- `src/mock/initialEnvelope.ts`
  - 只承担最小启动壳子
  - 不再承载真实业务详情
  - 初始 `allowedEvents` 只保留 `init_event`

Python：

- `python/patch_service.py`
  - 本地 HTTP patch 服务入口
  - 监听 `127.0.0.1:8000`
  - `/health` 用于健康检查
  - `/api/patch-plan` 由 Vite proxy 转发

- `python/agent_patch_builders/workflow_definition.py`
  - Python 事件契约和 `allowedEvents` 推导
  - 优先读取 generated 配置

- `python/agent_patch_builders/app_config_loader.py`
  - Python 侧 generated 配置加载器

- `python/agent_patch_builders/workflow_action_builders.py`
  - 业务事件到 patch 的主要 builders

- `python/agent_patch_builders/section_builders.py`
  - UI section builders

- `python/tests/`
  - `test_patch_builders.py`
  - `test_workflow_transition_contracts.py`
  - `test_app_compiler.py`
  - `test_generated_config_loading.py`

业务配置与编译：

- `apps/warning-review.app.yaml`
  - 当前预警核查工作台 DSL 源文件

- `tools/app_compiler.py`
  - CLI 编译/组装工具
  - 将 DSL 编译到 `generated/`

- `generated/warning_review_workbench/app.normalized.json`
  - 前端和 Python 当前共同加载的规范化配置

- `generated/warning_review_workbench/frontend/workflow-definition.generated.ts`
  - 生成的前端契约参考产物

- `generated/warning_review_workbench/python/workflow_definition.generated.py`
  - 生成的 Python 契约参考产物

- `generated/warning_review_workbench/tests/test_transition_contracts.generated.py`
  - 生成的阶段流转契约测试骨架

文档：

- `README.md`
- `HANDOVER.md`
- `docs/warning-review-workbench-dev-guide.md`
- `AGENTS.md`
- `claud.md`

## 当前页面结构

主页面常见 section：

- `sec_overview`：预警情况详情，`key_value`
- `sec_table_demo`：关联台账，`data_table`
- `sec_main_review`：核查方向，`checklist` + `text_input` + `button_group`
- `sec_review_report`：核查报告，`text`
- `sec_report_actions`：报告后续处理按钮
- `sec_report_edit`：核查报告修改子流程
- `sec_add_review_direction`：报告阶段新增核查方向输入区
- `sec_risk_identification`：风险认定
- `sec_action_plan`：行动计划
- `sec_resolution_result_no_risk`：无风险结果
- `sec_resolution_result_with_action`：有风险并完成行动计划后的结果

## allowedEvents 生命周期

初始壳子：

```ts
allowedEvents: ["init_event"]
```

初始化完成后：

- `toggle_check`
- `add_checklist_item`
- `Risk_Check_Event`
- `open_detail`

报告阶段：

- `edit_report`
- `add_review_direction_after_report`
- `enter_risk_identification`
- `open_detail`

报告修改中：

- `save_report_revision`
- `cancel_report_revision`
- `open_detail`

报告阶段新增核查方向输入中：

- `submit_new_direction_after_report`
- `cancel_add_direction`
- `open_detail`

风险认定阶段：

- `set_risk_decision`
- `update_risk_reason`
- `resolve_no_risk`
- `confirm_risk_identification`
- `open_detail`

行动计划阶段：

- `toggle_action_item`
- `add_action_item`
- `confirm_action_plan`
- `open_detail`

完成后：

- `open_detail`

## 业务配置工具

启动前端后，页面右上角可切换：

```text
运行台 / 配置工具
```

配置工具当前支持：

- 查看和编辑应用基本信息
- 查看 context 字段
- 编辑阶段标题、说明、`allowedEvents`、`visibleSections`
- 编辑事件基础信息、允许状态、处理程序
- 查看 section 与 widget 绑定
- 做基础引用校验
- 查看编译前检查、生成 CLI 编译命令、确认预计产物
- 导出当前内存配置为 YAML

限制：

- 当前不会直接写回 `apps/warning-review.app.yaml`
- 当前不会在浏览器内直接执行本地 Python
- 导出后仍需手动保存 DSL 并运行 compiler

## 编译和 generated 配置

编译命令：

```powershell
python tools\app_compiler.py apps\warning-review.app.yaml
```

生成目录：

```text
generated/warning_review_workbench/
```

当前 runtime 已加载：

- 前端：`src/workflow/appConfig.ts`
- Python：`python/agent_patch_builders/app_config_loader.py`

重要边界：

- generated 配置用于事件契约、初始 context 默认值、`allowedEvents` 推导
- 复杂业务 patch builder 仍由手写 Python 代码负责
- compiler 当前不会自动覆盖 `src/` 或 `python/` 下的人工维护文件

## 本地运行

启动 Python patch 服务：

```powershell
cd C:\Users\PC\Documents\Codex\2026-04-24\github\agent-ui-vue\python
python patch_service.py
```

健康检查：

```powershell
curl http://127.0.0.1:8000/health
```

启动前端：

```powershell
cd C:\Users\PC\Documents\Codex\2026-04-24\github\agent-ui-vue
npm run dev
```

注意：如果前端出现 `connect ECONNREFUSED 127.0.0.1:8000`，说明 Python patch 服务没有启动或端口不通。

## 测试与检查

Python 回归：

```powershell
python -m unittest discover -s python/tests -p "test_*.py"
```

TypeScript 检查：

```powershell
.\node_modules\.bin\vue-tsc.cmd --noEmit
```

应用 DSL 编译：

```powershell
python tools\app_compiler.py apps\warning-review.app.yaml
```

常规改动后建议至少跑：

1. Python 回归测试
2. TypeScript 检查
3. DSL 编译

## 调试顺序

页面没有按预期更新时，按这个顺序排查：

1. 当前 `allowedEvents` 是否包含目标事件
2. 事件日志里是否出现该事件
3. Python 服务是否收到事件
4. Python 是否通过事件契约校验
5. Python 是否返回 patch
6. 前端 `applyPatches()` 是否成功更新 `WorkflowEnvelope`
7. `WorkflowContext` 是否被正确写入
8. section / component 是否因为 key 策略正确重渲染

辅助观察：

- 右下角 `Allowed Events`
- 右下角 `Action Plan Debug`
- Python 服务日志中的 `event_type`、`state`、`allowed_events`、`patch_count`

## 维护约束

后续维护请遵守：

1. 不要在 widget 内直接改 `envelope`
2. 新行为优先定义为 `WorkflowEvent`
3. 所有 UI 更新优先走 patch
4. 业务真实状态优先写入 `WorkflowContext`
5. 新阶段优先通过 `state + visibleSections + allowedEvents` 建模
6. 不要把真实业务详情重新写回 `initialEnvelope.ts`
7. 事件契约需要同时考虑前端和 Python 入口
8. generated 配置优先作为契约来源，但不要让 compiler 覆盖人工维护代码
9. Python patch builders 要按业务动作拆分，避免堆成超长分支函数
10. 修改 renderer key 策略、报告阶段按钮、`allowedEvents` 时要重点回归

## 建议回归路径

每次做流程相关改动后，至少手动回归：

1. 页面加载后自动触发 `init_event`
2. 预警情况详情回填
3. 核查方向显示正确
4. 核查阶段新增核查方向可回写
5. 执行核查后生成 `sec_review_report` 和 `sec_report_actions`
6. 修改核查报告可进入 `sec_report_edit`
7. 保存或取消报告修改可回到报告阶段
8. 报告阶段新增核查方向可打开、提交、刷新报告、回到报告阶段
9. 进入风险认定后，无风险路径可解警闭环
10. 有风险路径可进入行动计划
11. 行动计划中勾选、新增、确认后完成任务
12. 配置工具可打开、校验、导出，并展示编译页

## 当前风险点

- 右下角调试面板仍是临时诊断能力，不一定适合生产形态
- 配置工具当前仅内存编辑，尚未接入保存/一键编译
- generated 产物是稳定契约输出，但复杂业务 patch builder 仍是手写代码
- renderer 层已有较强 key 策略，改 section/component 更新逻辑时要谨慎
- 报告阶段按钮和子流程是高关注区域，容易受 `allowedEvents` 和重渲染影响

## 推荐下一步

1. 给业务配置工具增加“保存 DSL”能力，最好通过本地 dev API 执行，不在浏览器直接写文件
2. 在配置工具中接入真实编译日志和编译结果展示
3. 清理右下角临时调试面板，改成可开关的开发诊断模式
4. 继续把 Python patch builders 按业务动作拆分
5. 增加前端联调/端到端回归测试
