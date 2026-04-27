import type { WorkflowEnvelope } from "../types/workflow";

export const initialEnvelope: WorkflowEnvelope = {
  id: "wf_risk_review_001",
  version: "1.0.0",
  state: "reviewing",
  allowedEvents: ["toggle_check", "submit_decision"],
  riskSummary: {
    level: "medium",
    summary: "当前请求存在中等合规风险，需要审核人完成最终确认。",
    details: [
      "该供应商为新接入对象，历史交易记录较少。",
      "合同条款中包含两项人工覆盖条件。",
      "材料包基本齐全，但仍缺少政策声明确认。",
    ],
  },
  messages: [
    {
      id: "msg_001",
      role: "agent",
      title: "智能体评估",
      body: "初步审核已完成，请在最终批准前确认检查清单项。",
      tone: "info",
      timestamp: "09:12",
    },
    {
      id: "msg_002",
      role: "system",
      title: "运行时",
      body: "当前界面由工作流信封和 Schema 驱动渲染。",
      tone: "success",
      timestamp: "09:13",
    },
  ],
  page: {
    id: "page_risk_review",
    title: "智能体审核工作台",
    description: "一个由 Schema 驱动的运行时界面，用于承接智能体决策、用户交互与 Patch 更新。",
    sections: [
      {
        id: "sec_overview",
        title: "请求概览",
        description: "智能体为当前审核任务提供的关键上下文信息。",
        components: [
          {
            id: "cmp_intro",
            type: "text",
            props: {
              content:
                "这个工作台由工作流 Schema 驱动，而不是写死在页面里的业务逻辑。",
              variant: "body",
            },
          },
          {
            id: "cmp_alert",
            type: "alert",
            props: {
              title: "需要审核人关注",
              description:
                "检测到人工覆盖路径，因此智能体在完成最终处理前必须获得审核人确认。",
              tone: "warning",
            },
          },
          {
            id: "cmp_kv",
            type: "key_value",
            props: {
              items: [
                { label: "案件编号", value: "RV-20314" },
                { label: "申请方", value: "Northwind Supply Co." },
                { label: "智能体置信度", value: "0.82" },
              ],
            },
          },
          {
            id: "cmp_badges",
            type: "badge_list",
            props: {
              items: ["人工覆盖", "新供应商", "政策声明待补充"],
              tone: "warning",
            },
          },
        ],
      },
      {
        id: "sec_main_review",
        title: "审核清单",
        description: "每一次交互都会产生工作流事件，并交由运行时处理。",
        components: [
          {
            id: "cmp_checklist",
            type: "checklist",
            props: {
              action: {
                eventType: "toggle_check",
              },
              items: [
                {
                  id: "item_identity",
                  label: "已核验供应商身份与注册信息",
                  description: "将注册编号与权威数据源进行交叉比对。",
                  checked: true,
                },
                {
                  id: "item_override",
                  label: "已审核人工覆盖原因说明",
                  description: "确保例外处理原因已有文档记录。",
                  checked: false,
                },
                {
                  id: "item_policy",
                  label: "已确认政策声明材料齐备",
                  description: "在最终结论回传给智能体前必须完成此项确认。",
                  checked: false,
                },
              ],
            },
          },
          {
            id: "cmp_actions",
            type: "button_group",
            props: {
              actions: [
                {
                  label: "批准",
                  eventType: "submit_decision",
                  payload: { decision: "approve" },
                  buttonType: "primary",
                },
                {
                  label: "退回修改",
                  eventType: "submit_decision",
                  payload: { decision: "revise" },
                  buttonType: "warning",
                },
              ],
            },
          },
        ],
      },
      {
        id: "sec_audit",
        title: "审计面板",
        description: "智能体提取出的结构化事实，供人工审核参考。",
        components: [
          {
            id: "cmp_audit",
            type: "audit_panel",
            props: {
              records: [
                { label: "材料覆盖率", value: "8 / 9 份文件", status: "warning" },
                { label: "制裁名单筛查", value: "未命中", status: "success" },
                { label: "历史例外次数", value: "过去 12 个月 2 次", status: "info" },
              ],
            },
          },
        ],
      },
    ],
  },
};
