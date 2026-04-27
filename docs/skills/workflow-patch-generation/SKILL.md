---
name: workflow-patch-generation
description: 为 agent-driven workflow UI runtime 生成经过校验的 PatchOperation 数组。当 Codex 或某个 Agent 需要把当前 WorkflowEnvelope、WorkflowEvent 以及可选业务上下文转换成最小合法 patch，而不是返回整页 schema 时使用。适用于工作流状态迁移、section 替换、风险摘要更新、消息插入、允许事件更新等 patch 规划任务。
---

# 工作流 Patch 生成

生成 patch 计划，不要直接返回完整页面。

## 输入契约

规划前先读取：

- `WorkflowEnvelope envelope`
- `WorkflowEvent event`
- 可选 `businessContext`
- 可选 `policyContext`

把 `envelope` 视为当前 UI 状态的唯一真相。

## 输出契约

返回符合下列结构的 JSON：

```json
{
  "patches": [],
  "rationale": "",
  "warnings": []
}
```

要求：

- `patches` 必须是 `PatchOperation[]`
- `rationale` 用 1-3 句话解释工作流迁移原因
- `warnings` 可选，仅在存在额外风险或策略提醒时返回

详细规则见：

- `references/patch-rules.md`
- `references/workflow-transition-patterns.md`
- `references/output-schema.md`

## 规划步骤

按这个顺序思考：

1. 读取 `envelope.state` 和 `envelope.allowedEvents`
2. 判断 `event.type` 当前是否允许执行
3. 判断目标工作流状态应该如何迁移
4. 选择表达该迁移所需的最小 patch 集
5. 返回前验证 section 引用和 state 值是否合法

## 强制约束

- 优先输出最小合法 patch 集
- 不要返回完整 envelope
- 不要修改无关 section
- `replace_section.sectionId` 与 `replace_section.value.id` 必须一致
- 发生工作流阶段变化时优先使用 `set_state`
- 需要控制后续交互权限时使用 `set_allowed_events`
- 需要向用户反馈时使用 `prepend_message`

## 非法事件规则

如果事件在当前状态下不合法，不要强行推进状态迁移。

优先返回保守 patch，一般只通过 `prepend_message` 反馈该事件被拒绝。

## Patch 选择启发式

优先顺序：

1. `set_state`
2. `replace_section`
3. `prepend_message`
4. `set_allowed_events`
5. `set_risk_summary`
6. `append_section`
7. `remove_section`

只有在界面确实需要增长时才使用 `append_section`。  
只有在 section 应彻底消失，而不是转换内容时才使用 `remove_section`。

## 最终自检

返回前确认：

- 每个 patch 都是合法操作
- patch 顺序是合理的
- 结果可以应用到当前 envelope
- rationale 与 patches 完全一致
