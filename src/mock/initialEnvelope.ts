import type { WorkflowEnvelope } from "../types/workflow";

export const initialEnvelope: WorkflowEnvelope = {
  id: "wf_risk_review_001",
  version: "1.0.0",
  state: "reviewing",
  allowedEvents: ["toggle_check", "submit_decision", "open_detail"],
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
      title: "运行时提示",
      body: "当前界面由工作流信封和 Schema 驱动渲染。",
      tone: "success",
      timestamp: "09:13",
    },
  ],
  page: {
    id: "page_risk_review",
    title: "智能体审核工作台",
    description:
      "一个由 Schema 驱动的运行时界面，用于承接智能体决策、用户交互与 Patch 更新。",
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
                "这个工作台由工作流 Schema 驱动，而不是把业务逻辑写死在页面里。",
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
              layout: "grid",
              columns: 3,
              minColumnWidth: 220,
              items: [
                { label: "案件编号", value: "RV-20314" },
                { label: "申请方", value: "Northwind Supply Co." },
                { label: "智能体置信度", value: "0.82" },
                { label: "风险等级", value: "中风险" },
                { label: "审核阶段", value: "审核中" },
                { label: "策略状态", value: "待确认" },
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
        id: "sec_table_demo",
        title: "审批列表",
        description: "演示更接近真实业务的审批列表，包括状态、金额、优先级和操作列。",
        components: [
          {
            id: "cmp_table_demo",
            type: "data_table",
            props: {
              stripe: true,
              border: true,
              size: "default",
              emptyText: "暂无审批数据",
              columns: [
                {
                  key: "caseId",
                  label: "案件编号",
                  type: "text",
                  minWidth: 140,
                },
                {
                  key: "applicant",
                  label: "申请方",
                  type: "text",
                  minWidth: 180,
                },
                {
                  key: "approvalStatus",
                  label: "审批状态",
                  type: "tag",
                  minWidth: 120,
                  tagMap: {
                    pending: { label: "待审核", tone: "warning" },
                    escalated: { label: "升级复核", tone: "danger" },
                    ready: { label: "可直接通过", tone: "success" },
                  },
                },
                {
                  key: "riskLevel",
                  label: "风险等级",
                  type: "tag",
                  minWidth: 120,
                  tagMap: {
                    low: { label: "低风险", tone: "success" },
                    medium: { label: "中风险", tone: "warning" },
                    high: { label: "高风险", tone: "danger" },
                  },
                },
                {
                  key: "amount",
                  label: "申请金额",
                  type: "number",
                  format: "currency",
                  currency: "CNY",
                  align: "right",
                  minWidth: 140,
                },
                {
                  key: "confidence",
                  label: "置信度",
                  type: "number",
                  format: "percent",
                  align: "right",
                  minWidth: 120,
                },
                {
                  key: "owner",
                  label: "当前负责人",
                  type: "text",
                  minWidth: 120,
                },
                {
                  key: "priority",
                  label: "优先级",
                  type: "tag",
                  minWidth: 110,
                  tagMap: {
                    p1: { label: "P1", tone: "danger" },
                    p2: { label: "P2", tone: "warning" },
                    p3: { label: "P3", tone: "info" },
                  },
                },
                {
                  key: "updatedAt",
                  label: "最近更新时间",
                  type: "date",
                  format: "datetime",
                  minWidth: 180,
                },
                {
                  key: "note",
                  label: "审核备注",
                  type: "text",
                  minWidth: 280,
                  multiline: true,
                },
                {
                  key: "actions",
                  label: "操作",
                  type: "action",
                  minWidth: 120,
                  actions: [
                    {
                      label: "查看详情",
                      eventType: "open_detail",
                      buttonType: "primary",
                      rowFieldMap: {
                        caseId: "caseId",
                        applicant: "applicant",
                        amount: "amount",
                      },
                    },
                  ],
                },
              ],
              rows: [
                {
                  caseId: "RV-20314",
                  applicant: "Northwind Supply Co.",
                  approvalStatus: "pending",
                  riskLevel: "medium",
                  amount: 328000,
                  confidence: 0.82,
                  owner: "李敏",
                  priority: "p2",
                  updatedAt: "2026-04-27T10:20:00+08:00",
                  note: "该案件存在人工覆盖条件，建议在批准前补充政策声明确认材料。",
                },
                {
                  caseId: "RV-20315",
                  applicant: "Acme Logistics Asia",
                  approvalStatus: "escalated",
                  riskLevel: "high",
                  amount: 1245000,
                  confidence: 0.64,
                  owner: "张晨",
                  priority: "p1",
                  updatedAt: "2026-04-27T10:45:00+08:00",
                  note: "历史交易次数较少，且供应商为首次接入对象，建议升级人工复核级别。",
                },
                {
                  caseId: "RV-20316",
                  applicant: "Harbor Medical Devices",
                  approvalStatus: "ready",
                  riskLevel: "low",
                  amount: 89600,
                  confidence: 0.93,
                  owner: "王蕾",
                  priority: "p3",
                  updatedAt: "2026-04-27T11:05:00+08:00",
                  note: "材料完整，制裁筛查通过，可进入自动化后续流程。",
                },
              ],
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
