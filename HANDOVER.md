# 项目交接说明

## 1. 项目定位

`agent-ui-vue` 不是传统的“页面组件直接维护业务状态”的前端项目，而是一套 **Agent-driven UI Runtime Engine** 的前端原型。

当前主场景为：

**预警核查工作台**

核心链路是：

```text
页面初始化 / 用户交互
-> WorkflowEvent
-> Runtime
-> Patch Planner
-> PatchOperation[]
-> applyPatches()
-> UI 更新
```

这意味着：

- UI 由 JSON Schema 驱动
- 前端组件不直接改业务状态
- 所有 UI 更新都走 patch
- 运行时根据 `state + section + allowedEvents` 控制工作流阶段

## 2. 当前已实现能力

当前仓库已经支持：

- Vue3 + Element Plus 工作台骨架
- schema-driven renderer
- widget registry
- patch engine
- 本地 HTTP Python patch 服务
- Python patch-builders
- 启动时自动触发 `init_event`
- 回填预警详情与核查方向
- 新增核查方向
- 执行核查并生成核查报告
- 报告阶段后续处理入口
- 风险认定
- 无风险解警闭环
- 有风险 -> 行动计划 -> 任务完成闭环

## 3. 关键目录与职责

### 协议定义

- [src/types/workflow.ts](C:/Users/PC/Documents/Codex/2026-04-24/github/agent-ui-vue/src/types/workflow.ts)

定义：

- `WorkflowEnvelope`
- `WorkflowEvent`
- `PatchOperation`
- `WorkflowState`
- `UISection`
- `UIComponent`

### Runtime

- [src/composables/useWorkflowRuntime.ts](C:/Users/PC/Documents/Codex/2026-04-24/github/agent-ui-vue/src/composables/useWorkflowRuntime.ts)

职责：

- 持有 `envelope`
- 记录 `eventLog`
- 调用 planner
- 应用 patch
- 管理 runtime 状态

### Patch Engine

- [src/utils/patch.ts](C:/Users/PC/Documents/Codex/2026-04-24/github/agent-ui-vue/src/utils/patch.ts)

职责：

- 统一应用 patch
- 保证状态更新入口唯一

### 前端 Planner 适配层

- [src/agent/HttpPatchPlannerModel.ts](C:/Users/PC/Documents/Codex/2026-04-24/github/agent-ui-vue/src/agent/HttpPatchPlannerModel.ts)

职责：

- 向 Python patch 服务发起 `/api/patch-plan` 请求

### Python patch 服务

- [python/patch_service.py](C:/Users/PC/Documents/Codex/2026-04-24/github/agent-ui-vue/python/patch_service.py)

职责：

- 接收 `envelope + event`
- 分发到 Python patch-builders
- 返回 patch plan

### Python patch-builders

- [python/agent_patch_builders](C:/Users/PC/Documents/Codex/2026-04-24/github/agent-ui-vue/python/agent_patch_builders)

职责：

- 按业务动作生成 patch
- 支撑本地联调
- 支撑未来 Python Agent 集成

### Renderer

- [src/components/renderer/PageRenderer.vue](C:/Users/PC/Documents/Codex/2026-04-24/github/agent-ui-vue/src/components/renderer/PageRenderer.vue)
- [src/components/renderer/SectionRenderer.vue](C:/Users/PC/Documents/Codex/2026-04-24/github/agent-ui-vue/src/components/renderer/SectionRenderer.vue)
- [src/components/renderer/ComponentRenderer.vue](C:/Users/PC/Documents/Codex/2026-04-24/github/agent-ui-vue/src/components/renderer/ComponentRenderer.vue)
- [src/components/renderer/registry.ts](C:/Users/PC/Documents/Codex/2026-04-24/github/agent-ui-vue/src/components/renderer/registry.ts)

职责：

- 将 Schema 解释为真实 Vue 组件树

### Widgets

- [src/components/widgets](C:/Users/PC/Documents/Codex/2026-04-24/github/agent-ui-vue/src/components/widgets)

原则：

- 只渲染
- 只发事件
- 不直接改业务状态

### 初始壳子

- [src/mock/initialEnvelope.ts](C:/Users/PC/Documents/Codex/2026-04-24/github/agent-ui-vue/src/mock/initialEnvelope.ts)

当前角色：

- 只提供最小启动壳子
- 占位 section
- 占位数据
- `allowedEvents: ["init_event"]`

真实业务内容不再写死在这里，而是由初始化 patch 回填。

## 4. 动态 allowedEvents 生命周期

这是当前项目非常重要的一条规则。

### 启动前

`initialEnvelope.ts` 里只保留：

```ts
allowedEvents: ["init_event"]
```

含义：

- 页面刚启动时，只允许初始化
- 不允许提前勾选核查方向
- 不允许提前新增核查方向
- 不允许提前执行核查

### 初始化完成后

初始化 patch 下发：

- `toggle_check`
- `add_checklist_item`
- `Risk_Check_Event`
- `open_detail`

### 报告阶段

执行核查后，下发：

- `edit_report`
- `add_review_direction_after_report`
- `enter_risk_identification`
- `open_detail`

### 风险认定阶段

进入风险认定后，下发：

- `set_risk_decision`
- `update_risk_reason`
- `resolve_no_risk`
- `confirm_risk_identification`
- `open_detail`

### 行动计划阶段

确认“有风险”后，下发：

- `toggle_action_item`
- `add_action_item`
- `confirm_action_plan`
- `open_detail`

### 任务完成后

当前会收紧为：

- `open_detail`

### 维护原则

以后新增工作流阶段时，继续遵守：

1. `initialEnvelope` 只保留最小启动事件
2. 初始化后通过 patch 开放真实业务事件
3. 阶段切换时再通过 patch 切换事件白名单

## 5. 当前页面与流程

### 页面结构

当前主要 section：

- `sec_overview`：预警情况详情
- `sec_table_demo`：关联台账
- `sec_main_review`：核查方向
- `sec_review_report`：核查报告
- `sec_report_actions`：报告后续处理
- `sec_risk_identification`：风险认定
- `sec_action_plan`：行动计划
- `sec_resolution_result_no_risk`：无风险处置结果
- `sec_resolution_result_with_action`：有风险行动结果

### 当前主流程

#### 路径 A：无风险

```text
init_event
-> 核查方向回填
-> 执行核查
-> 生成核查报告
-> 进入风险认定
-> 选择无风险
-> 填写风险认定说明
-> 确认无风险并解警
-> 任务完成
```

#### 路径 B：有风险

```text
init_event
-> 核查方向回填
-> 执行核查
-> 生成核查报告
-> 进入风险认定
-> 选择有风险
-> 填写风险认定说明
-> 确认有风险
-> 进入行动计划
-> 勾选 / 新增行动事项
-> 确认行动计划
-> 任务完成
```

## 6. 当前关键事件

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

## 7. 本地运行

### 安装前端依赖

```powershell
npm install
```

### 启动前端

```powershell
cd C:\Users\PC\Documents\Codex\2026-04-24\github\agent-ui-vue
npm run dev
```

### 启动 Python patch 服务

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

## 8. 调试建议

### 1. 看右下角 Allowed Events

当前页面右下角有调试面板，可以实时看到当前 `allowedEvents`，非常适合排查：

- 初始化后事件有没有放开
- 阶段切换后事件有没有切换
- 某个按钮为什么是灰的

### 2. 看 Python patch 服务日志

默认 `INFO`：

- 事件类型
- 事件 id
- 当前 state
- 当前 allowedEvents
- patch 数量

打开 `DEBUG`：

```powershell
$env:PATCH_SERVICE_LOG_LEVEL="DEBUG"
python patch_service.py
```

### 3. 重点排查顺序

如果页面没反应，建议按这个顺序看：

1. 当前 `allowedEvents` 是否包含目标事件
2. 前端 widget 是否可点
3. Python 服务是否收到事件
4. 返回 patch 是否符合预期
5. `applyPatches()` 是否成功应用

## 9. 维护约束

请尽量遵守：

1. 不要在 widget 里直接改 `envelope`
2. 新行为优先设计成 `WorkflowEvent`
3. 所有 UI 变化优先走 patch
4. 新阶段优先通过 `state + section + allowedEvents` 建模
5. 新 section 优先使用 `replace_section / append_section / remove_section`
6. 真实业务数据不要重新写死回 `initialEnvelope.ts`

## 10. 建议手测路径

每次改动后至少验证：

1. 页面加载后是否自动触发 `init_event`
2. “预警情况详情”是否回填
3. “核查方向”是否显示服务端建议
4. 新增核查方向后是否回写 checklist
5. 点击“执行核查”后是否出现：
   - `sec_review_report`
   - `sec_report_actions`
6. 进入风险认定后：
   - 无风险是否能解警
   - 有风险是否能进入行动计划
7. 行动计划里：
   - 勾选事项是否回写
   - 新增事项是否回写
   - 确认后是否任务完成

## 11. 后续建议

推荐下一步：

1. 实现“修改核查报告”
2. 实现“报告阶段新增核查方向并重新核查”
3. 补更多 Python 单元测试
4. 把报告从单一 `text` 拆成结构化 section
5. 补前端联调自动化测试
