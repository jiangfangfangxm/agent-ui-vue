# Patch 规则

## 允许的操作

- `set_state`
- `replace_section`
- `append_section`
- `remove_section`
- `prepend_message`
- `set_allowed_events`
- `set_risk_summary`

不要输出其他操作名。

## 各操作语义

### set_state

用途：

- 表达工作流阶段迁移

要求：

- `value` 必须是合法 `WorkflowState`

### replace_section

用途：

- 原位替换某个 section 的内容

要求：

- `sectionId` 必须存在
- `value.id` 必须与 `sectionId` 一致

### append_section

用途：

- 在页面尾部增加一个新的 section

要求：

- `value.id` 不能与现有 section 重复

### remove_section

用途：

- 删除某个已有 section

要求：

- `sectionId` 必须存在

### prepend_message

用途：

- 插入用户可见消息
- 提示 patch 已应用
- 提示事件被拦截或被拒绝

### set_allowed_events

用途：

- 更新当前允许的事件集合

建议：

- 当工作流进入终态时，通常应清空允许事件

### set_risk_summary

用途：

- 更新风险摘要区域

要求：

- `level` 必须是合法 `RiskLevel`
- `summary` 和 `details` 应与新的风险判断保持一致
