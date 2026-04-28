/**
 * 当前 demo 页面使用的 mock 工作流信封。
 * 这里定义页面初始 schema、允许事件和示例数据，是理解交互效果的最快入口。
 * 适合放演示数据和原型流程，不适合放正式业务逻辑。
 */
import type { WorkflowEnvelope } from "../types/workflow";

export const initialEnvelope: WorkflowEnvelope = {
  id: "wf_warning_review_001",
  version: "1.0.0",
  state: "reviewing",
  allowedEvents: [
    "init_event",
    "toggle_check",
    "add_checklist_item",
    "Risk_Check_Event",
    "open_detail",
  ],
  riskSummary: {
    level: "medium",
    summary: "当前存在一条待核查预警，建议先完成详情初始化与人工复核。",
    details: [
      "预警详情将在页面初始化时通过 init_event 回填。",
      "核查方向将由服务端建议并写入核查清单。",
    ],
  },
  messages: [
    {
      id: "msg_001",
      role: "system",
      title: "工作台已启动",
      body: "页面加载后将自动触发 init_event，并由服务端返回 patch 更新预警详情与核查方向。",
      tone: "info",
      timestamp: "09:12",
    },
  ],
  page: {
    id: "page_warning_review",
    title: "预警核查工作台",
    description: "一个由 Schema 驱动的预警核查运行时界面，用于承接初始化回填、人工核查与 Patch 更新。",
    sections: [
      {
        id: "sec_overview",
        title: "预警情况详情",
        description: "该区域在页面启动后会通过 init_event 触发的 patch 回填。",
        components: [
          {
            id: "cmp_warning_detail",
            type: "key_value",
            props: {
              layout: "grid",
              columns: 3,
              minColumnWidth: 220,
              items: [
                { label: "预警编号", value: "-" },
                { label: "客户名称", value: "-" },
                { label: "预警类型", value: "-" },
                { label: "命中时间", value: "-" },
                { label: "风险等级", value: "-" },
                { label: "当前状态", value: "-" },
              ],
            },
          },
        ],
      },
      {
        id: "sec_table_demo",
        title: "关联台账",
        description: "演示与当前预警相关的审批台账与关联案件。",
        components: [
          {
            id: "cmp_table_demo",
            type: "data_table",
            props: {
              stripe: true,
              border: true,
              size: "default",
              emptyText: "暂无关联数据",
              columns: [
                { key: "caseId", label: "案件编号", type: "text", minWidth: 140 },
                { key: "applicant", label: "客户名称", type: "text", minWidth: 180 },
                {
                  key: "approvalStatus",
                  label: "处理状态",
                  type: "tag",
                  minWidth: 120,
                  tagMap: {
                    pending: { label: "待核查", tone: "warning" },
                    escalated: { label: "升级复核", tone: "danger" },
                    ready: { label: "可直接处置", tone: "success" },
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
                  label: "关联金额",
                  type: "number",
                  format: "currency",
                  currency: "CNY",
                  align: "right",
                  minWidth: 140,
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
                  label: "备注",
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
                  caseId: "WARN-REL-001",
                  applicant: "华东星联贸易有限公司",
                  approvalStatus: "pending",
                  riskLevel: "high",
                  amount: 328000,
                  updatedAt: "2026-04-28T09:20:00+08:00",
                  note: "近 7 日交易频率明显异常，需结合受益人信息进一步核查。",
                },
                {
                  caseId: "WARN-REL-002",
                  applicant: "华东星联贸易有限公司",
                  approvalStatus: "escalated",
                  riskLevel: "medium",
                  amount: 1245000,
                  updatedAt: "2026-04-28T09:45:00+08:00",
                  note: "历史交易对手存在高风险地区关联，建议升级复核。",
                },
              ],
            },
          },
        ],
      },
      {
        id: "sec_main_review",
        title: "核查方向",
        description: "初始化后会由服务端 patch 回填核查建议，人工也可以继续追加核查方向。",
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
                  id: "item_placeholder",
                  label: "等待服务端返回核查建议",
                  description: "页面启动后将通过 init_event 更新为真实核查方向。",
                  checked: false,
                },
              ],
            },
          },
          {
            id: "cmp_custom_check_input",
            type: "text_input",
            props: {
              eventType: "add_checklist_item",
              label: "新增核查方向",
              placeholder: "例如：核验交易对手与受益人是否存在隐性关联",
              buttonLabel: "添加到清单",
              helperText: "输入后会由运行时生成 patch，并把新的核查方向回写到当前 checklist。",
              clearOnSubmit: true,
            },
          },
          {
            id: "cmp_actions",
            type: "button_group",
            props: {
              actions: [
                {
                  label: "执行核查",
                  eventType: "Risk_Check_Event",
                  payload: { decision: "execute" },
                  buttonType: "primary",
                },
              ],
            },
          },
        ],
      },
      {
        id: "sec_audit",
        title: "审计面板",
        description: "智能体提取出的结构化事实，供人工核查参考。",
        components: [
          {
            id: "cmp_audit",
            type: "audit_panel",
            props: {
              records: [
                { label: "预警来源", value: "异常交易监测引擎", status: "info" },
                { label: "命中规则数", value: "3 条", status: "warning" },
                { label: "历史处置记录", value: "过去 12 个月 1 次", status: "success" },
              ],
            },
          },
        ],
      },
    ],
  },
};
