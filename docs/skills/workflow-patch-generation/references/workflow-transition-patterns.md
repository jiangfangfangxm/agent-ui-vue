# 工作流迁移模式

## toggle_check

输入特征：

- `event.type = "toggle_check"`
- payload 中通常包含 `itemId`

常见输出：

1. `replace_section("sec_main_review", updatedChecklistSection)`
2. `prepend_message(...)`

不要：

- 修改整个 page
- 清空 allowed events

## submit_decision / approve

输入特征：

- `event.type = "submit_decision"`
- `payload.decision = "approve"`

常见输出：

1. `set_state("presenting_result")`
2. `replace_section("sec_main_review", resultSection)`
3. `set_allowed_events([])`
4. `set_risk_summary(lowRiskSummary)`
5. `prepend_message(...)`

## submit_decision / revise

输入特征：

- `event.type = "submit_decision"`
- `payload.decision = "revise"`

常见输出：

1. `set_state("awaiting_revision")`
2. `replace_section("sec_main_review", revisionResultSection)`
3. `set_allowed_events([])`
4. `set_risk_summary(mediumRiskSummary)`
5. `prepend_message(...)`

## blocked event

输入特征：

- 当前 `allowedEvents` 不包含该事件

常见输出：

1. `prepend_message(systemWarning)`

不要：

- 强行迁移 state
- 强行替换 section

## risk escalation

适用场景：

- Agent 发现额外风险
- 用户动作触发新的审查条件

常见输出：

1. `set_risk_summary(highRiskSummary)`
2. `prepend_message(agentWarning)`
3. 必要时 `set_allowed_events(...)`
