# AGENTS.md

## 项目概览

`agent-ui-vue` 是一个 **Agent-driven UI Runtime Engine** 示例项目，当前主场景是：

- **预警核查工作台**

这个项目不是传统的“前端组件内部直接维护业务状态”的实现方式，而是把页面演化拆成一条清晰链路：

```text
页面初始化 / 用户操作
-> WorkflowEvent
-> Runtime
-> Patch Planner
-> PatchOperation[]
-> applyPatches()
-> WorkflowEnvelope
-> Renderer
-> UI 更新
```

核心原则：

- UI 由 `WorkflowEnvelope` 和 JSON Schema 驱动
- 组件层不直接修改业务状态
- 所有状态更新都通过 `PatchOperation[]`
- `allowedEvents` 控制当前阶段允许哪些交互

---

## 当前业务场景

当前工作台围绕“预警核查”流程展开，主要包含这些阶段：

1. 页面启动后自动触发 `init_event`
2. 服务端回填“预警情况详情”和“核查方向”
3. 用户执行核查，生成核查报告
4. 进入报告后续处理
5. 进入风险认定
6. 若为无风险：解警并完成任务
7. 若为有风险：进入行动计划并完成任务

---

## 关键目录

### 前端

- [src/App.vue](C:\Users\PC\Documents\Codex\2026-04-24\github\agent-ui-vue\src\App.vue)
  页面入口，挂载后自动触发 `init_event`

- [src/composables/useWorkflowRuntime.ts](C:\Users\PC\Documents\Codex\2026-04-24\github\agent-ui-vue\src\composables\useWorkflowRuntime.ts)
  Runtime 中枢，负责：
  - 持有 `WorkflowEnvelope`
  - 记录事件日志
  - 调用 planner
  - 应用 patch
  - 维护 runtime 状态

- [src/types/workflow.ts](C:\Users\PC\Documents\Codex\2026-04-24\github\agent-ui-vue\src\types\workflow.ts)
  核心协议定义：
  - `WorkflowEnvelope`
  - `WorkflowEvent`
  - `PatchOperation`
  - `WorkflowState`
  - `UISection`
  - `UIComponent`

- [src/utils/patch.ts](C:\Users\PC\Documents\Codex\2026-04-24\github\agent-ui-vue\src\utils\patch.ts)
  Patch Engine，唯一的前端状态变更入口

- [src/agent/HttpPatchPlannerModel.ts](C:\Users\PC\Documents\Codex\2026-04-24\github\agent-ui-vue\src\agent\HttpPatchPlannerModel.ts)
  前端通过 HTTP 调 Python patch 服务

- [src/components/renderer](C:\Users\PC\Documents\Codex\2026-04-24\github\agent-ui-vue\src\components\renderer)
  Schema 渲染层：
  - `PageRenderer.vue`
  - `SectionRenderer.vue`
  - `ComponentRenderer.vue`
  - `registry.ts`

- [src/components/widgets](C:\Users\PC\Documents\Codex\2026-04-24\github\agent-ui-vue\src\components\widgets)
  具体 widget 实现，例如：
  - `ChecklistWidget.vue`
  - `ButtonGroupWidget.vue`
  - `TextInputWidget.vue`
  - `KeyValueWidget.vue`
  - `DataTableWidget.vue`

- [src/mock/initialEnvelope.ts](C:\Users\PC\Documents\Codex\2026-04-24\github\agent-ui-vue\src\mock\initialEnvelope.ts)
  当前只承担“最小启动壳子”角色，不再承载真实业务详情

### Python 侧

- [python/patch_service.py](C:\Users\PC\Documents\Codex\2026-04-24\github\agent-ui-vue\python\patch_service.py)
  本地 HTTP patch 服务入口

- [python/agent_patch_builders](C:\Users\PC\Documents\Codex\2026-04-24\github\agent-ui-vue\python\agent_patch_builders)
  Python patch-builders，负责根据业务事件生成 patch

- [python/tests/test_patch_builders.py](C:\Users\PC\Documents\Codex\2026-04-24\github\agent-ui-vue\python\tests\test_patch_builders.py)
  Python 侧核心回归测试

### 文档

- [README.md](C:\Users\PC\Documents\Codex\2026-04-24\github\agent-ui-vue\README.md)
- [HANDOVER.md](C:\Users\PC\Documents\Codex\2026-04-24\github\agent-ui-vue\HANDOVER.md)
- [docs/Agent.md](C:\Users\PC\Documents\Codex\2026-04-24\github\agent-ui-vue\docs\Agent.md)

说明：当前 `README.md` 和 `HANDOVER.md` 存在明显编码污染，阅读时要留意。后续建议统一整理为 UTF-8 中文版。

---

## 当前页面结构

当前主页面通常包含这些 section：

- `sec_overview`
  - 预警情况详情
  - 使用 `key_value`

- `sec_table_demo`
  - 关联台账
  - 使用 `data_table`

- `sec_main_review`
  - 核查方向
  - 使用 `checklist` + `text_input` + `button_group`

- `sec_review_report`
  - 核查报告
  - 使用 `text`

- `sec_report_actions`
  - 报告后续处理
  - 3 个按钮：
    - 修改核查报告
    - 新增核查方向
    - 进入风险认定环节

- `sec_add_review_direction`
  - 报告阶段新增核查方向输入区

- `sec_risk_identification`
  - 风险认定

- `sec_action_plan`
  - 行动计划

- `sec_resolution_result_no_risk`
  - 无风险结果

- `sec_resolution_result_with_action`
  - 有风险并完成行动计划后的结果

---

## 当前工作流状态

当前 `WorkflowState` 主要有：

- `reviewing`
- `report_reviewing`
- `risk_identifying`
- `action_planning`
- `resolved_no_risk`
- `resolved_with_action`
- `presenting_result`
- `awaiting_revision`

其中当前预警核查主流程主要使用：

- `reviewing`
- `report_reviewing`
- `risk_identifying`
- `action_planning`
- `resolved_no_risk`
- `resolved_with_action`

---

## 当前重要事件

### 初始化阶段

- `init_event`

### 核查阶段

- `toggle_check`
- `add_checklist_item`
- `Risk_Check_Event`
- `open_detail`

### 报告阶段

- `edit_report`
- `add_review_direction_after_report`
- `submit_new_direction_after_report`
- `cancel_add_direction`
- `enter_risk_identification`

### 风险认定阶段

- `set_risk_decision`
- `update_risk_reason`
- `resolve_no_risk`
- `confirm_risk_identification`

### 行动计划阶段

- `toggle_action_item`
- `add_action_item`
- `confirm_action_plan`

---

## allowedEvents 生命周期

这个项目目前采用“最小启动事件 + 初始化后动态下发真实事件”的模式。

### 初始壳子

`initialEnvelope.ts` 中只保留：

```ts
allowedEvents: ["init_event"]
```

### 初始化完成后

通过 patch 下发：

- `toggle_check`
- `add_checklist_item`
- `Risk_Check_Event`
- `open_detail`

### 报告阶段

通过 patch 下发：

- `edit_report`
- `add_review_direction_after_report`
- `enter_risk_identification`
- `open_detail`

### 报告阶段新增核查方向输入中

通过 patch 临时切换为：

- `submit_new_direction_after_report`
- `cancel_add_direction`
- `open_detail`

### 风险认定阶段

通过 patch 切换为：

- `set_risk_decision`
- `update_risk_reason`
- `resolve_no_risk`
- `confirm_risk_identification`
- `open_detail`

### 行动计划阶段

通过 patch 切换为：

- `toggle_action_item`
- `add_action_item`
- `confirm_action_plan`
- `open_detail`

### 任务完成后

当前一般收敛为：

- `open_detail`

---

## 当前已实现的业务能力

### 1. 初始化

- 自动触发 `init_event`
- 回填预警情况详情
- 回填核查方向

### 2. 核查方向

- 勾选核查方向
- 新增核查方向
- 执行核查生成报告

### 3. 报告后续处理

- 展示 3 个后续处理按钮
- 报告阶段可新增核查方向
- 新增后会：
  - 更新 `sec_main_review`
  - 重新生成 `sec_review_report`
  - 移除输入区
  - 回到报告阶段事件集

### 4. 风险认定

- 进入风险认定
- 选择有风险/无风险
- 填写风险认定说明
- 无风险时可解警

### 5. 行动计划

- 有风险时自动展开行动计划区
- 勾选推荐行动
- 新增行动事项
- 确认行动计划
- 完成任务

---

## 已知问题 / 风险点

### 1. 文档编码问题

`README.md` 和 `HANDOVER.md` 当前可见明显乱码，后续需要统一重写。

### 2. 报告阶段按钮状态问题

最近在“报告后续处理”按钮禁用态上做过多轮排查和修复。  
当前代码已做过若干防抖和重建处理，但这一块属于高关注区域，后续改动后要重点回归。

### 3. 前端渲染复用问题

项目里为了处理 section / component 不刷新的问题，已经在 renderer 层引入了更强的 key 变化策略。  
后续改动 `section.components` 或 checklist items 时，要注意不要破坏现有的重渲染假设。

### 4. Debug 面板属于临时诊断能力

当前工作台右下角有：

- `Allowed Events`
- `Action Plan Debug`

它们对排查很有帮助，但不一定适合长期保留在生产形态中。

---

## 本地运行方式

### 前端

```powershell
cd C:\Users\PC\Documents\Codex\2026-04-24\github\agent-ui-vue
npm run dev
```

### Python patch 服务

```powershell
cd C:\Users\PC\Documents\Codex\2026-04-24\github\agent-ui-vue\python
python patch_service.py
```

### 健康检查

```powershell
curl http://127.0.0.1:8000/health
```

### Python 测试

```powershell
python -m unittest discover -s python/tests -p "test_*.py"
```

---

## 调试建议

### 1. 优先看右下角调试面板

观察：

- `Allowed Events`
- `Action Plan Debug`

### 2. 再看 Python 服务日志

日志重点关注：

- 收到的 `event_type`
- 当前 `state`
- 当前 `allowedEvents`
- `patch_count`

### 3. 排查顺序建议

如果页面没有按预期更新，按这个顺序排查：

1. 当前 `allowedEvents` 是否包含目标事件
2. 事件日志里是否出现该事件
3. Python 服务是否收到事件
4. Python 是否返回了 patch
5. 前端 `applyPatches()` 后是否更新了 `WorkflowEnvelope`
6. section / widget 是否真的重渲染

---

## 维护约束

后续维护时请尽量遵守：

1. 不要在 widget 内直接改 `envelope`
2. 新行为优先先定义成 `WorkflowEvent`
3. 所有 UI 更新优先走 patch
4. 新阶段优先通过 `state + section + allowedEvents` 建模
5. 真实业务数据不要重新写回 `initialEnvelope.ts`
6. 优先维护 Python patch-builders 的清晰职责，不要把所有分支堆成一个超长函数

---

## 建议回归路径

每次做改动后，至少回归：

1. 页面加载后是否自动触发 `init_event`
2. 预警情况详情是否回填
3. 核查方向是否正确显示
4. 新增核查方向（核查阶段）是否回写
5. 执行核查后是否生成：
   - `sec_review_report`
   - `sec_report_actions`
6. 报告阶段新增核查方向是否：
   - 打开输入区
   - 回写核查方向
   - 刷新报告
7. 风险认定的无风险路径是否闭环
8. 有风险路径是否进入行动计划
9. 行动计划中：
   - 勾选是否回写
   - 新增行动事项是否回写
   - 确认后是否完成任务

---

## 推荐下一步

当前最值得继续推进的方向：

1. 真正实现“修改核查报告”
2. 清理右下角临时调试面板
3. 把 README / HANDOVER 重写成无乱码中文版
4. 继续补前端联调回归测试
5. 把 Python patch-builders 进一步按业务动作拆分得更清晰

