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
    "submit_decision",
    "open_detail",
  ],
  riskSummary: {
    level: "medium",
    summary: "当前存在一条待核查预警，建议先完成详情初始化与人工复核。",
    details: [
      "预警详情将在页面初始化时通过 init_event 回填。",
      "核查过程中仍需结合审批列表与审核清单完成最终判断。",
    ],
  },
  messages: [
    {
      id: "msg_001",
      role: "system",
      title: "工作台已启动",
      body: "页面加载后将自动触发 init_event，并由服务端返回 patch 更新预警详情。",
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
                { key: "caseId", label: "案件编号", type: "text", minWidth: 140 },
                { key: "applicant", label: "申请方", type: "text", minWidth: 180 },
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
                { key: "owner", label: "当前负责人", type: "text", minWidth: 120 },
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
                {
                  id: "item_bank",
                  label: "已核验付款账户与开户主体一致",
                  description: "确认付款账户名称、开户主体与合同主体一致。",
                  checked: false,
                },
                {
                  id: "item_contract",
                  label: "已确认合同补充条款已归档",
                  description: "补充协议、例外条款和审批意见均应留痕归档。",
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
              label: "新增审核事项",
              placeholder: "例如：确认付款账户与开户主体一致",
              buttonLabel: "添加到清单",
              helperText: "输入后会由运行时生成 patch，并把新的审核事项回写到当前 checklist。",
              clearOnSubmit: true,
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
