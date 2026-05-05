<script setup lang="ts">
import { computed, onBeforeUnmount, onMounted, ref } from "vue";
import type { FraudProgressItem, FraudReportTab } from "../../types/workflow";
import type { WidgetPropsOfType } from "./widgetContract";

type FraudPanelType = "FraudAuditPanel" | "status_tree" | "radar_chart" | "markdown_tabs";
const PANEL_LINK_STORAGE_KEY = "fraud_panel_link_payload_v1";

interface PanelLinkPayload {
  categoryKey: string;
  categoryLabel: string;
  serialNo: string;
  selectedScenarioIds: string[];
  selectedScenarioLabels: string[];
  startedAt: string;
}

const props = defineProps<
  WidgetPropsOfType<"FraudAuditPanel"> |
    WidgetPropsOfType<"status_tree"> |
    WidgetPropsOfType<"radar_chart"> |
    WidgetPropsOfType<"markdown_tabs">
>();

const defaultProgressItems: FraudProgressItem[] = [
  { id: "credit_scene_1", name: "征信场景-1", status: "pending", detail: "等待开始解读" },
  { id: "credit_scene_2", name: "征信场景-2", status: "pending", detail: "等待开始解读" },
  { id: "device_scene_1", name: "设备场景-1", status: "pending", detail: "等待开始解读" },
  { id: "device_scene_2", name: "设备场景-2", status: "pending", detail: "等待开始解读" },
  { id: "enterprise_scene_1", name: "工商场景-1", status: "pending", detail: "等待开始解读" },
  { id: "operation_scene_1", name: "经营场景-1", status: "pending", detail: "等待开始解读" },
  { id: "internal_scene_1", name: "行内场景-1", status: "pending", detail: "等待开始解读" },
  { id: "multimodal_scene_1", name: "跨模态场景-1", status: "pending", detail: "等待开始解读" },
  { id: "intelligence_scene_1", name: "情报场景-1", status: "pending", detail: "等待开始解读" },
];

const defaultReportTabs: FraudReportTab[] = [
  {
    key: "credit",
    label: "征信核查",
    markdownHtml: `
      <h3>## 征信核查摘要</h3>
      <p>申请人近 6 个月还款行为出现 <mark>异常</mark> 脉冲，单月还款额峰值高于历史均值 4.1 倍，且集中在账单日前 1 天。</p>
      <p>多头借贷侧识别到 <mark>共债率3.5</mark>，高于策略阈值 2.2，疑似通过短期资金腾挪制造稳定还款假象。</p>
      <h4>### AI 指标提取</h4>
      <ul>
        <li>征信查询密度指数：0.86（高）</li>
        <li>还款平滑度偏离：+173%</li>
        <li>授信重叠度：71%</li>
        <li>逾期迁徙波动：M1->M3 跳跃 2 次</li>
      </ul>
      <h4>### LLM 解读</h4>
      <p>模型认为申请人存在“短周期资金回补 + 共债掩饰”组合行为，建议将其纳入高风险分层并要求补充资金来源证明。</p>
      <h4>### 功能点（9）</h4>
      <ul>
        <li>征信美化识别</li><li>共债穿透分析</li><li>M3+迁徙检测</li><li>还款轨迹拆解</li><li>查询密度热区</li><li>授信重叠画像</li><li>代偿链路回流</li><li>历史违约回看</li><li>征信漂白样式库</li>
      </ul>
    `,
  },
  {
    key: "device",
    label: "设备核查",
    markdownHtml: `
      <h3>## 设备核查摘要</h3>
      <p>设备图谱显示核心终端在 72 小时内切换 5 个账号，命中“设备共用”高危模板；且触控轨迹呈脚本化特征，疑似自动化操作。</p>
      <p>网络侧出现代理链抖动与 GPS 偏移共振，存在跨地域仿真登录迹象。</p>
      <h4>### AI 指标提取</h4>
      <ul>
        <li>设备共用强度：9.2/10</li>
        <li>模拟环境置信度：92%</li>
        <li>行为节律异常评分：81</li>
        <li>IP 漂移频次：14 次/24h</li>
      </ul>
      <h4>### LLM 解读</h4>
      <p>设备侧证据与征信风险形成交叉增强，推断存在组织化中介代操作可能，应触发二级人工复核。</p>
      <h4>### 功能点（9）</h4>
      <ul>
        <li>设备共用图谱</li><li>模拟器识别</li><li>Root/Jailbreak 检测</li><li>代理链追踪</li><li>触控节律分析</li><li>多开容器检测</li><li>设备漂移告警</li><li>跨终端一致性校验</li><li>地理欺骗识别</li>
      </ul>
    `,
  },
  {
    key: "enterprise",
    label: "工商核查",
    markdownHtml: `
      <h3>## 工商核查摘要</h3>
      <p>主体存续正常，但近 9 个月法人与高管变更频次异常，股权结构出现短链拆分，存在规避审查迹象。</p>
      <h4>### 功能点（9）</h4>
      <ul>
        <li>工商存续核验</li><li>股权穿透</li><li>受益人识别</li><li>司法涉诉归集</li><li>裁判文书交叉</li><li>历史变更追踪</li><li>空壳模式识别</li><li>经营范围校验</li><li>注册地址可信评估</li>
      </ul>
    `,
  },
  {
    key: "operation",
    label: "经营核查",
    markdownHtml: `
      <h3>## 经营核查摘要</h3>
      <p>营收流水与开票规模不匹配，供应链高度集中，库存与销售数据出现断点，经营稳定性较弱。</p>
      <h4>### 功能点（9）</h4>
      <ul>
        <li>流水真实性校验</li><li>开票一致性检验</li><li>供应链集中度分析</li><li>断供风险预估</li><li>库存周转健康度</li><li>三账一致性检测</li><li>税务连续性检测</li><li>经营季节性建模</li><li>毛利波动诊断</li>
      </ul>
    `,
  },
  {
    key: "internal",
    label: "行内核查",
    markdownHtml: `
      <h3>## 行内核查摘要</h3>
      <p>复贷周期缩短、夜间交易高频、渠道来源异常，符合“高压资金周转客户”风险模式。</p>
      <h4>### 功能点（9）</h4>
      <ul>
        <li>历史借贷画像</li><li>复贷动机识别</li><li>夜间交易分析</li><li>同额拆分识别</li><li>渠道可信评分</li><li>中介导流检测</li><li>联系人关系网</li><li>担保网络风险</li><li>存量资产联动评估</li>
      </ul>
    `,
  },
  {
    key: "multimodal",
    label: "跨模态核查",
    markdownHtml: `
      <h3>## 跨模态核查摘要</h3>
      <p>证照、语音、视频三模态结果存在矛盾信号，数据真实性需继续核实。</p>
      <h4>### 功能点（9）</h4>
      <ul>
        <li>OCR 结构抽取</li><li>图文一致性校验</li><li>证照篡改检测</li><li>声纹同一性校验</li><li>语义情绪异常识别</li><li>活体动作校验</li><li>深伪概率评估</li><li>跨模态冲突检测</li><li>多模态证据融合</li>
      </ul>
    `,
  },
  {
    key: "intelligence",
    label: "情报核查",
    markdownHtml: `
      <h3>## 情报核查摘要</h3>
      <p>黑产威胁情报、舆情事件和社交身份扩散均存在高危命中，建议提升审核等级。</p>
      <h4>### 功能点（9）</h4>
      <ul>
        <li>黑产号码库命中</li><li>威胁 IP 识别</li><li>恶意设备标签</li><li>舆情事件关联</li><li>投诉聚类分析</li><li>暗网线索聚合</li><li>身份映射推理</li><li>社交扩散链路</li><li>团伙情报融合</li>
      </ul>
    `,
  },
  {
    key: "custom",
    label: "自定义核查",
    markdownHtml: `
      <h3>## 自定义核查摘要</h3>
      <p>专家策略与模型策略混合执行，灰度回放显示当前阈值仍可进一步提升召回。</p>
      <h4>### 功能点（9）</h4>
      <ul>
        <li>规则编排中心</li><li>专家策略管理</li><li>模型策略路由</li><li>阈值回放校准</li><li>A/B 灰度实验</li><li>误杀样本回收</li><li>策略版本对比</li><li>离线评估看板</li><li>可解释性报告导出</li>
      </ul>
    `,
  },
];

const panelType = computed(() => props.component.type as FraudPanelType);
const activeTab = ref("credit");
const panelLinkPayload = ref<PanelLinkPayload | null>(null);
const nowMs = ref(Date.now());
const STEP_DURATION_MS = 1500;
const maxParallel = ref(3);
let timer: ReturnType<typeof setInterval> | null = null;

function readPanelLinkPayload(): void {
  const raw = localStorage.getItem(PANEL_LINK_STORAGE_KEY);
  if (!raw) {
    panelLinkPayload.value = null;
    return;
  }
  try {
    panelLinkPayload.value = JSON.parse(raw) as PanelLinkPayload;
  } catch {
    panelLinkPayload.value = null;
  }
}

function handlePanelLinkUpdated(): void {
  readPanelLinkPayload();
}

onMounted(() => {
  readPanelLinkPayload();
  window.addEventListener("fraud-panel-link-updated", handlePanelLinkUpdated);
  timer = setInterval(() => {
    nowMs.value = Date.now();
  }, 250);
});

onBeforeUnmount(() => {
  window.removeEventListener("fraud-panel-link-updated", handlePanelLinkUpdated);
  if (timer) {
    clearInterval(timer);
    timer = null;
  }
});

const hasStarted = computed(
  () =>
    !!panelLinkPayload.value &&
    panelLinkPayload.value.selectedScenarioIds &&
    panelLinkPayload.value.selectedScenarioIds.length > 0,
);

const progressItems = computed(() => {
  const baseline = props.component.props.progressItems ?? defaultProgressItems;
  if (!hasStarted.value || !panelLinkPayload.value) {
    return baseline.map((item) => ({
      ...item,
      status: "pending" as const,
      detail: "等待开始解读",
    }));
  }
  const selectedIds = panelLinkPayload.value.selectedScenarioIds;
  const elapsed = nowMs.value - new Date(panelLinkPayload.value.startedAt).getTime();
  const selectedOrder = new Map(selectedIds.map((id, index) => [id, index]));

  return baseline.map((item, index) => {
    if (!selectedIds.includes(item.id)) {
      return {
        ...item,
        status: "pending" as const,
        detail: "未选中本场景",
      };
    }
    const order = selectedOrder.get(item.id) ?? index;
    const batchIndex = Math.floor(order / maxParallel.value);
    const startAt = batchIndex * STEP_DURATION_MS;
    const finishAt = (batchIndex + 1) * STEP_DURATION_MS;
    if (elapsed < startAt) {
      return {
        ...item,
        status: "pending" as const,
        detail: "已纳入队列，等待并行槽位",
      };
    }
    if (elapsed < finishAt) {
      return {
        ...item,
        status: "processing" as const,
        detail: "AI 正在解读中",
      };
    }
    return {
      ...item,
      status: "success" as const,
      detail: "已完成解读",
    };
  });
});

const reportTabs = computed(() => {
  if (!hasStarted.value) {
    return defaultReportTabs.map((tab) => ({
      ...tab,
      markdownHtml: `
        <h3>## ${tab.label}摘要</h3>
        <p>当前尚未开始解读。请先在上方核查工具箱勾选场景并点击“开始智能核查”。</p>
      `,
    }));
  }
  return props.component.props.reportTabs ?? defaultReportTabs;
});

const riskMetrics = computed(() =>
  hasStarted.value
    ? [
        { key: "fraud", label: "欺诈可能性", score: 85 },
        { key: "willingness", label: "还款意愿", score: 30 },
        { key: "ability", label: "还款能力", score: 45 },
        { key: "authenticity", label: "数据真实性", score: 60 },
      ]
    : [
        { key: "fraud", label: "欺诈可能性", score: 0 },
        { key: "willingness", label: "还款意愿", score: 0 },
        { key: "ability", label: "还款能力", score: 0 },
        { key: "authenticity", label: "数据真实性", score: 0 },
      ],
);
const riskTagType = computed(() => (hasStarted.value ? "danger" : "info"));
const riskTagText = computed(() => (hasStarted.value ? "高风险" : "待解读"));

const radarPoints = computed(() => {
  const centerX = 100;
  const centerY = 100;
  const maxRadius = 78;
  const angles = [-90, 0, 90, 180];

  return riskMetrics.value
    .map((item, index) => {
      const radians = (angles[index] * Math.PI) / 180;
      const radius = (item.score / 100) * maxRadius;
      const x = centerX + Math.cos(radians) * radius;
      const y = centerY + Math.sin(radians) * radius;
      return `${x.toFixed(2)},${y.toFixed(2)}`;
    })
    .join(" ");
});

function statusTagType(status: FraudProgressItem["status"]): "success" | "warning" | "info" {
  if (status === "success") {
    return "success";
  }
  if (status === "processing") {
    return "warning";
  }
  return "info";
}

const showStatusTree = computed(
  () => panelType.value === "FraudAuditPanel" || panelType.value === "status_tree",
);
const showRadar = computed(
  () => panelType.value === "FraudAuditPanel" || panelType.value === "radar_chart",
);
const showTabs = computed(
  () => panelType.value === "FraudAuditPanel" || panelType.value === "markdown_tabs",
);
</script>

<template>
  <div class="fraud-audit-panel" :class="`mode-${panelType}`">
    <div class="parallel-config">
      <span>并发槽位</span>
      <el-select v-model="maxParallel" size="small" style="width: 120px">
        <el-option :value="1" label="1 并发" />
        <el-option :value="2" label="2 并发" />
        <el-option :value="3" label="3 并发" />
        <el-option :value="4" label="4 并发" />
      </el-select>
    </div>

    <aside v-if="showStatusTree" class="status-tree">
      <div class="block-title">多模式并行进度</div>
      <el-timeline>
        <el-timeline-item
          v-for="item in progressItems"
          :key="item.id"
          :type="statusTagType(item.status)"
          :hollow="item.status !== 'success'"
          :class="`status-${item.status}`"
        >
          <div class="timeline-row">
            <strong>{{ item.name }}</strong>
            <el-tag size="small" :type="statusTagType(item.status)">
              {{ item.status === "success" ? "已完成" : item.status === "processing" ? "进行中" : "待执行" }}
            </el-tag>
          </div>
          <p>{{ item.detail }}</p>
        </el-timeline-item>
      </el-timeline>
    </aside>

    <section v-if="showRadar || showTabs" class="main-report">
      <div v-if="showRadar" class="risk-board">
        <div class="board-left">
          <div class="block-title">四维风险雷达图</div>
          <svg viewBox="0 0 200 200" class="radar-svg">
            <polygon points="100,20 180,100 100,180 20,100" class="radar-frame" />
            <polygon points="100,40 160,100 100,160 40,100" class="radar-frame light" />
            <line x1="100" y1="20" x2="100" y2="180" class="radar-axis" />
            <line x1="20" y1="100" x2="180" y2="100" class="radar-axis" />
            <polygon :points="radarPoints" class="radar-data" />
          </svg>
        </div>
        <div class="board-right">
          <div class="block-title">综合风险定级</div>
          <el-tag :type="riskTagType" size="large">{{ riskTagText }}</el-tag>
          <ul class="metric-list">
            <li v-for="metric in riskMetrics" :key="metric.key">
              <span>{{ metric.label }}</span>
              <strong>{{ metric.score }}</strong>
            </li>
          </ul>
        </div>
      </div>

      <div v-if="showTabs" class="markdown-report">
        <div class="block-title">AI 解读与分类报告</div>
        <el-tabs v-model="activeTab" type="border-card">
          <el-tab-pane
            v-for="tab in reportTabs"
            :key="tab.key"
            :name="tab.key"
            :label="tab.label"
          >
            <article class="markdown-content" v-html="tab.markdownHtml" />
          </el-tab-pane>
        </el-tabs>
      </div>
    </section>
  </div>
</template>

<style scoped>
.fraud-audit-panel {
  display: grid;
  gap: 14px;
}

.parallel-config {
  display: flex;
  align-items: center;
  gap: 10px;
  justify-content: flex-end;
  font-size: 13px;
  color: #52606d;
}

.mode-FraudAuditPanel {
  grid-template-columns: 340px minmax(0, 1fr);
}

.status-tree,
.risk-board,
.markdown-report {
  border: 1px solid #dce6f3;
  border-radius: 16px;
  background: #fff;
}

.status-tree {
  max-height: 860px;
  overflow: auto;
  padding: 14px;
}

.main-report {
  display: grid;
  gap: 14px;
}

.risk-board {
  display: grid;
  grid-template-columns: 320px minmax(0, 1fr);
  padding: 14px;
}

.board-left,
.board-right {
  display: grid;
  align-content: start;
  gap: 12px;
}

.block-title {
  margin: 0;
  font-size: 14px;
  font-weight: 700;
  color: #3a4a5f;
}

.timeline-row {
  display: flex;
  justify-content: space-between;
  gap: 10px;
  align-items: center;
}

.timeline-row + p {
  margin: 8px 0 0;
  color: #687888;
}

.status-processing :deep(.el-timeline-item__content) {
  animation: pulse-running 1.2s ease-in-out infinite;
}

@keyframes pulse-running {
  0% { opacity: 0.66; }
  50% { opacity: 1; }
  100% { opacity: 0.66; }
}

.radar-svg {
  width: 220px;
  height: 220px;
}

.radar-frame {
  fill: rgb(52 152 219 / 0.08);
  stroke: #9ab6d4;
  stroke-width: 1.4;
}

.radar-frame.light {
  fill: rgb(52 152 219 / 0.14);
}

.radar-axis {
  stroke: #b6c8db;
  stroke-width: 1.2;
}

.radar-data {
  fill: rgb(231 76 60 / 0.35);
  stroke: #e74c3c;
  stroke-width: 2;
}

.metric-list {
  margin: 0;
  padding: 0;
  list-style: none;
  display: grid;
  gap: 8px;
}

.metric-list li {
  display: flex;
  justify-content: space-between;
  border: 1px solid #e3ebf6;
  border-radius: 10px;
  padding: 8px 10px;
}

.metric-list strong {
  color: #cf3f36;
}

.markdown-report {
  padding: 14px;
}

.markdown-content :deep(h3),
.markdown-content :deep(h4) {
  margin-top: 4px;
}

.markdown-content :deep(p),
.markdown-content :deep(li) {
  line-height: 1.7;
  color: #304253;
}

.markdown-content :deep(mark) {
  background: #ffe49a;
  padding: 1px 4px;
  border-radius: 4px;
  color: #7a2400;
}

@media (max-width: 1200px) {
  .mode-FraudAuditPanel,
  .risk-board {
    grid-template-columns: 1fr;
  }
}
</style>
