<script setup lang="ts">
import { computed, reactive, ref, watchEffect } from "vue";
import distilledSample from "../../../distilled_rules/distilled_sample.json";
import type { ConfigWorkbenchCategory, WorkflowEventInput } from "../../types/workflow";
import type { WidgetPropsOfType } from "./widgetContract";

interface DistilledFeature {
  feature_name: string;
  technical_logic: string;
  filter_condition: string;
}

interface ScenarioItem {
  id: string;
  categoryKey: string;
  sceneName: string;
  nlDescription: string;
  requiredByDefault: boolean;
  dslFeatures: DistilledFeature[];
}

interface RuleBinding {
  id: string;
  ruleName: string;
  scenarioIds: string[];
}

interface CustomerCase {
  serialNo: string;
  customerName: string;
  baseMustCheckIds: string[];
  matchedRuleIds: string[];
  mustCheckIds: string[];
  riskLevel: "高风险" | "中风险" | "低风险";
  featureSignals: Record<string, string | number>;
}

interface ConfigPersistPayload {
  scenarioCatalog: ScenarioItem[];
  ruleBindings: RuleBinding[];
  customerCases: CustomerCase[];
}

const props = defineProps<WidgetPropsOfType<"ConfigWorkbench">>();
const emit = defineEmits<{ dispatch: [event: WorkflowEventInput] }>();
const categories: Array<{ key: string; label: string }> = [
  { key: "credit", label: "征信核查" },
  { key: "device", label: "设备核查" },
  { key: "enterprise", label: "工商核查" },
  { key: "operation", label: "经营核查" },
  { key: "internal", label: "行内核查" },
  { key: "multimodal", label: "跨模态核查" },
  { key: "intelligence", label: "情报核查" },
  { key: "custom", label: "自定义核查" },
];
const configurableCategories = categories.filter((item) => item.key !== "custom");
const PANEL_LINK_STORAGE_KEY = "fraud_panel_link_payload_v1";
const featureList = (distilledSample.features as DistilledFeature[] | undefined) ?? [];
const featureCursor = ref(0);
const CONFIG_STORAGE_KEY = "fraud_workbench_config_v1";

function deepClone<T>(value: T): T {
  return JSON.parse(JSON.stringify(value)) as T;
}

function pickFeatureGroup(size: number): DistilledFeature[] {
  const selected: DistilledFeature[] = [];
  for (let i = 0; i < size; i += 1) {
    const feature = featureList[featureCursor.value % featureList.length];
    if (feature) {
      selected.push(feature);
    }
    featureCursor.value += 1;
  }
  return selected;
}

const scenarioCatalog = ref<ScenarioItem[]>(
  configurableCategories.flatMap((category, categoryIndex) =>
    [1, 2, 3].map((sceneIndex) => ({
      id: `${category.key}_scene_${sceneIndex}`,
      categoryKey: category.key,
      sceneName: `${category.label}场景-${sceneIndex}`,
      nlDescription: `核验客户在${category.label}下的异常模式，重点关注资金、行为和关联关系是否匹配已知风险画像。`,
      requiredByDefault: categoryIndex % 2 === 0 && sceneIndex === 1,
      dslFeatures: pickFeatureGroup(2),
    })),
  ),
);

const categoryLabelMap = Object.fromEntries(categories.map((item) => [item.key, item.label]));

const defaultCategories = computed<ConfigWorkbenchCategory[]>(() =>
  categories.map((category) => {
    const scenes = scenarioCatalog.value.filter((item) => item.categoryKey === category.key);
    return {
      key: category.key,
      label: category.label,
      autoRequired: scenes
        .filter((item) => item.requiredByDefault)
        .map((item) => `${item.sceneName}：${item.nlDescription}`),
      optional: scenes
        .filter((item) => !item.requiredByDefault)
        .map((item) => `${item.sceneName}：${item.nlDescription}`),
    };
  }),
);

const normalizedCategories = computed<ConfigWorkbenchCategory[]>(() => {
  const external = props.component.props.categories;
  return external && external.length > 0 ? external : defaultCategories.value;
});
const activeCategoryKey = ref(normalizedCategories.value[0]?.key ?? "credit");
const optionalSelection = reactive<Record<string, string[]>>({});
const queryText = ref("");
const appTab = ref("workbench");

const ruleBindings = ref<RuleBinding[]>([
  {
    id: "rule_high_debt_cluster",
    ruleName: "高负债与资金异常联动规则",
    scenarioIds: ["credit_scene_1", "operation_scene_1"],
  },
  {
    id: "rule_device_alert_merge",
    ruleName: "设备异常与预警联动规则",
    scenarioIds: ["device_scene_1", "intelligence_scene_1"],
  },
]);
const newRuleName = ref("");
const selectedScenarioIds = ref<string[]>([]);

const customerCases = ref<CustomerCase[]>([
  {
    serialNo: "BL2026-0001",
    customerName: "测试客户A",
    baseMustCheckIds: ["credit_scene_1"],
    matchedRuleIds: ["rule_high_debt_cluster", "rule_device_alert_merge"],
    mustCheckIds: ["credit_scene_1", "device_scene_1", "intelligence_scene_1"],
    riskLevel: "高风险",
    featureSignals: { ft1: 12, ft2: 986000, ft9: 325000, ft24: "red" },
  },
  {
    serialNo: "BL2026-0002",
    customerName: "测试客户B",
    baseMustCheckIds: ["credit_scene_2", "operation_scene_1"],
    matchedRuleIds: ["rule_high_debt_cluster"],
    mustCheckIds: ["credit_scene_2", "operation_scene_1"],
    riskLevel: "中风险",
    featureSignals: { ft3: 4, ft10: 52, ft12: 178000, ft15: 2.1 },
  },
  {
    serialNo: "BL2026-0003",
    customerName: "测试客户C",
    baseMustCheckIds: ["device_scene_2", "internal_scene_1", "multimodal_scene_1"],
    matchedRuleIds: ["rule_device_alert_merge"],
    mustCheckIds: ["device_scene_2", "internal_scene_1", "multimodal_scene_1"],
    riskLevel: "高风险",
    featureSignals: { ft21: 45, ft22: 62, ft23: 5, ft20: 14 },
  },
  {
    serialNo: "BL2026-0004",
    customerName: "测试客户D",
    baseMustCheckIds: ["enterprise_scene_1", "operation_scene_2"],
    matchedRuleIds: ["rule_high_debt_cluster"],
    mustCheckIds: ["enterprise_scene_1", "operation_scene_2"],
    riskLevel: "中风险",
    featureSignals: { ft5: 7, ft6: 190000, ft19: 16, ft20: 3 },
  },
  {
    serialNo: "BL2026-0005",
    customerName: "测试客户E",
    baseMustCheckIds: ["enterprise_scene_2"],
    matchedRuleIds: [],
    mustCheckIds: ["enterprise_scene_2"],
    riskLevel: "低风险",
    featureSignals: { ft11: 2, ft14: 1, ft16: 0.8, ft24: "blue" },
  },
  {
    serialNo: "BL2026-0006",
    customerName: "测试客户F",
    baseMustCheckIds: ["credit_scene_1", "device_scene_1", "operation_scene_1"],
    matchedRuleIds: ["rule_high_debt_cluster", "rule_device_alert_merge"],
    mustCheckIds: ["credit_scene_1", "device_scene_1", "operation_scene_1"],
    riskLevel: "高风险",
    featureSignals: { ft1: 15, ft7: 9, ft9: 560000, ft24: "red" },
  },
  {
    serialNo: "BL2026-0007",
    customerName: "测试客户G",
    baseMustCheckIds: ["internal_scene_2", "intelligence_scene_2"],
    matchedRuleIds: ["rule_device_alert_merge"],
    mustCheckIds: ["internal_scene_2", "intelligence_scene_2"],
    riskLevel: "中风险",
    featureSignals: { ft19: 9, ft20: 2, ft23: 1, ft24: "orange" },
  },
  {
    serialNo: "BL2026-0008",
    customerName: "测试客户H",
    baseMustCheckIds: ["multimodal_scene_2", "internal_scene_3"],
    matchedRuleIds: [],
    mustCheckIds: ["multimodal_scene_2", "internal_scene_3"],
    riskLevel: "低风险",
    featureSignals: { ft21: 3, ft22: 4, ft15: 1.1, ft16: 1.0 },
  },
]);
const activeSerialNo = ref(customerCases.value[0]?.serialNo ?? "");
const openAiKey = ref("");
const selectedSceneIdForJudge = ref(scenarioCatalog.value[0]?.id ?? "");
const llmPrompt = ref("请判断该客户是否符合当前场景，并输出核心特征命中与小结。");
const llmResult = ref("");
const llmLoading = ref(false);
const editingSceneId = ref(scenarioCatalog.value[0]?.id ?? "");
const editingFeaturesText = ref("");
const importError = ref("");
const importInputRef = ref<HTMLInputElement | null>(null);
const intelligenceMailbox = ref("intel-inbox@outside.example.com");
const intelligenceQuestion = ref("");
const intelligenceRequests = ref<
  Array<{
    id: string;
    serialNo: string;
    question: string;
    mailbox: string;
    status: "sent" | "done";
    result: string;
  }>
>([]);

const defaultScenarioCatalog = deepClone(scenarioCatalog.value);
const defaultRuleBindings = deepClone(ruleBindings.value);
const defaultCustomerCases = deepClone(customerCases.value);

watchEffect(() => {
  for (const category of categories) {
    const optionalIds = scenarioCatalog.value
      .filter((item) => item.categoryKey === category.key && !item.requiredByDefault)
      .map((item) => item.id);
    if (!optionalSelection[category.key]) {
      optionalSelection[category.key] = [];
    } else {
      optionalSelection[category.key] = optionalSelection[category.key].filter((id) =>
        optionalIds.includes(id),
      );
    }
  }
});

const validScenarioIdSet = computed(() => new Set(scenarioCatalog.value.map((item) => item.id)));

watchEffect(() => {
  const ruleMap = new Map(ruleBindings.value.map((rule) => [rule.id, rule]));
  for (const customer of customerCases.value) {
    const fromRules = customer.matchedRuleIds.flatMap((ruleId) => {
      const rule = ruleMap.get(ruleId);
      return rule ? rule.scenarioIds : [];
    });
    customer.mustCheckIds = [...new Set([...customer.baseMustCheckIds, ...fromRules])].filter(
      (id) => validScenarioIdSet.value.has(id),
    );
  }
});

const activeCategory = computed(
  () =>
    normalizedCategories.value.find((item) => item.key === activeCategoryKey.value) ??
    normalizedCategories.value[0],
);
const activeCase = computed(() =>
  customerCases.value.find((item) => item.serialNo === activeSerialNo.value),
);
const activeCategoryScenes = computed(() =>
  scenarioCatalog.value.filter((item) => item.categoryKey === activeCategoryKey.value),
);
const isCustomCategory = computed(() => activeCategoryKey.value === "custom");
const isIntelligenceCategory = computed(() => activeCategoryKey.value === "intelligence");
const activeRequiredScenes = computed(() =>
  activeCategoryScenes.value.filter((item) => item.requiredByDefault),
);
const activeOptionalScenes = computed(() =>
  activeCategoryScenes.value.filter((item) => !item.requiredByDefault),
);
const activeMustCheck = computed(() =>
  scenarioCatalog.value.filter((item) => activeCase.value?.mustCheckIds.includes(item.id)),
);
const sceneOptions = computed(() =>
  configurableCategories.flatMap((category) =>
    scenarioCatalog.value
      .filter((item) => item.categoryKey === category.key)
      .map((item) => ({
        id: item.id,
        label: `${category.label} / ${item.sceneName}`,
      })),
  ),
);
const editingScene = computed(() =>
  scenarioCatalog.value.find((item) => item.id === editingSceneId.value),
);
const selectedSceneForJudge = computed(() =>
  scenarioCatalog.value.find((item) => item.id === selectedSceneIdForJudge.value),
);
const activeCustomerRuleIds = computed<string[]>({
  get: () => activeCase.value?.matchedRuleIds ?? [],
  set: (value) => {
    if (activeCase.value) {
      activeCase.value.matchedRuleIds = [...value];
    }
  },
});

watchEffect(() => {
  if (editingScene.value) {
    editingFeaturesText.value = JSON.stringify(editingScene.value.dslFeatures, null, 2);
  }
});

function addScenario(): void {
  const index = scenarioCatalog.value.length + 1;
  const category = configurableCategories[index % configurableCategories.length];
  const featureA = featureList[index % featureList.length];
  const featureB = featureList[(index + 1) % featureList.length];
  scenarioCatalog.value.push({
    id: `custom_scene_${index}`,
    categoryKey: category.key,
    sceneName: `新增场景-${index}`,
    nlDescription: "请补充该场景的自然语言描述和判定规则。",
    requiredByDefault: false,
    dslFeatures: [featureA, featureB].filter(Boolean) as DistilledFeature[],
  });
}

function buildConfigPayload(): ConfigPersistPayload {
  return {
    scenarioCatalog: scenarioCatalog.value,
    ruleBindings: ruleBindings.value,
    customerCases: customerCases.value,
  };
}

function applyConfigPayload(payload: ConfigPersistPayload): void {
  scenarioCatalog.value = deepClone(payload.scenarioCatalog);
  ruleBindings.value = deepClone(payload.ruleBindings);
  customerCases.value = deepClone(payload.customerCases);
  if (!customerCases.value.some((item) => item.serialNo === activeSerialNo.value)) {
    activeSerialNo.value = customerCases.value[0]?.serialNo ?? "";
  }
}

function saveToLocalStorage(): void {
  localStorage.setItem(CONFIG_STORAGE_KEY, JSON.stringify(buildConfigPayload()));
  llmResult.value = "配置已保存到本地 localStorage。";
}

function resetToDefaults(): void {
  applyConfigPayload({
    scenarioCatalog: deepClone(defaultScenarioCatalog),
    ruleBindings: deepClone(defaultRuleBindings),
    customerCases: deepClone(defaultCustomerCases),
  });
  llmResult.value = "已恢复默认配置。";
}

function loadFromLocalStorage(): void {
  const raw = localStorage.getItem(CONFIG_STORAGE_KEY);
  if (!raw) {
    llmResult.value = "本地没有可加载的配置。";
    return;
  }
  try {
    applyConfigPayload(JSON.parse(raw) as ConfigPersistPayload);
    llmResult.value = "已从 localStorage 加载配置。";
  } catch (error) {
    llmResult.value = error instanceof Error ? error.message : "本地配置解析失败。";
  }
}

function exportConfigJson(): void {
  const blob = new Blob([JSON.stringify(buildConfigPayload(), null, 2)], {
    type: "application/json",
  });
  const url = URL.createObjectURL(blob);
  const anchor = document.createElement("a");
  anchor.href = url;
  anchor.download = "fraud-workbench-config.json";
  anchor.click();
  URL.revokeObjectURL(url);
}

function triggerImportJson(): void {
  importInputRef.value?.click();
}

async function onImportFileChange(event: Event): Promise<void> {
  const target = event.target as HTMLInputElement;
  const file = target.files?.[0];
  importError.value = "";
  if (!file) return;
  try {
    const text = await file.text();
    applyConfigPayload(JSON.parse(text) as ConfigPersistPayload);
    llmResult.value = "配置 JSON 导入成功。";
  } catch (error) {
    importError.value = error instanceof Error ? error.message : "导入失败。";
  } finally {
    target.value = "";
  }
}

function applySceneFeatureJson(): void {
  if (!editingScene.value) return;
  try {
    const parsed = JSON.parse(editingFeaturesText.value) as DistilledFeature[];
    if (!Array.isArray(parsed)) {
      throw new Error("DSL 特征必须是数组");
    }
    editingScene.value.dslFeatures = parsed;
  } catch (error) {
    llmResult.value = error instanceof Error ? error.message : "DSL 特征 JSON 解析失败。";
  }
}

function addRuleBinding(): void {
  if (!newRuleName.value.trim() || selectedScenarioIds.value.length === 0) return;
  const newRuleId = `rule_${Date.now()}`;
  ruleBindings.value.push({
    id: newRuleId,
    ruleName: newRuleName.value.trim(),
    scenarioIds: [...selectedScenarioIds.value],
  });
  if (activeCase.value && !activeCase.value.matchedRuleIds.includes(newRuleId)) {
    activeCase.value.matchedRuleIds.push(newRuleId);
  }
  newRuleName.value = "";
  selectedScenarioIds.value = [];
}

async function sendIntelligenceRequest(): Promise<void> {
  if (!activeCase.value) return;
  if (!intelligenceQuestion.value.trim()) {
    llmResult.value = "请先填写要查询的情报问题。";
    return;
  }

  const requestId = `intel_${Date.now()}`;
  intelligenceRequests.value.unshift({
    id: requestId,
    serialNo: activeCase.value.serialNo,
    question: intelligenceQuestion.value.trim(),
    mailbox: intelligenceMailbox.value,
    status: "sent",
    result: "已发送至行外邮箱，等待小龙虾 cron 拉取并回传 web_search 结果。",
  });

  const currentQuestion = intelligenceQuestion.value.trim();
  intelligenceQuestion.value = "";

  await new Promise((resolve) => setTimeout(resolve, 1200));
  const item = intelligenceRequests.value.find((req) => req.id === requestId);
  if (item) {
    item.status = "done";
    item.result = `模拟回传结果：关于“${currentQuestion}”，已抓取到 3 条外部情报，含 1 条高危舆情与 1 条关联主体负面。`;
  }
}

function onStartAudit(): void {
  const category = activeCategory.value;
  if (!category) return;
  const selectedScenarioIds = [
    ...activeRequiredScenes.value.map((item) => item.id),
    ...(optionalSelection[category.key] ?? []),
  ];
  const selectedScenarioLabels = scenarioCatalog.value
    .filter((item) => selectedScenarioIds.includes(item.id))
    .map((item) => item.sceneName);

  const linkPayload = {
    categoryKey: activeCategoryKey.value,
    categoryLabel: category.label,
    serialNo: activeSerialNo.value,
    selectedScenarioIds,
    selectedScenarioLabels,
    startedAt: new Date().toISOString(),
  };
  localStorage.setItem(PANEL_LINK_STORAGE_KEY, JSON.stringify(linkPayload));
  window.dispatchEvent(
    new CustomEvent("fraud-panel-link-updated", {
      detail: linkPayload,
    }),
  );

  const eventType =
    (props.component.props.startEventType ?? "handle_nl_query") === "open_detail"
      ? "handle_nl_query"
      : (props.component.props.startEventType ?? "handle_nl_query");
  emit("dispatch", {
    type: eventType,
    componentId: props.component.id,
    payload: {
      naturalQuery: queryText.value,
      category: category.label,
      serialNo: activeSerialNo.value,
      selectedScenarios: selectedScenarioIds,
    },
  });
}

async function runLlm(): Promise<void> {
  const scene = selectedSceneForJudge.value;
  if (!scene) {
    llmResult.value = "请选择要判定的场景。";
    return;
  }
  if (!openAiKey.value.trim()) {
    llmResult.value = "请先输入 OpenAI Key。";
    return;
  }
  llmLoading.value = true;
  llmResult.value = "";
  try {
    const response = await fetch("/api/llm-interpret", {
      method: "POST",
      headers: {
        "Content-Type": "application/json",
      },
      body: JSON.stringify({
        apiKey: openAiKey.value.trim(),
        model: "gpt-4o-mini",
        messages: [
          {
            role: "system",
            content:
              "你是反欺诈复核助手。请基于场景DSL特征和自然语言描述，判断客户是否符合该场景，输出：核心命中特征、是否符合、小结建议。",
          },
          {
            role: "user",
            content: `业务流水号：${activeSerialNo.value}
客户：${activeCase.value?.customerName ?? "未知"}
风险等级：${activeCase.value?.riskLevel ?? "未知"}
场景分类：${categoryLabelMap[scene.categoryKey]}
场景名称：${scene.sceneName}
场景自然语言描述：${scene.nlDescription}
DSL特征：
${JSON.stringify(scene.dslFeatures, null, 2)}
客户特征快照：
${JSON.stringify(activeCase.value?.featureSignals ?? {}, null, 2)}
问题：${llmPrompt.value}`,
          },
        ],
        temperature: 0.2,
      }),
    });
    if (!response.ok) {
      const detail = await response.text();
      throw new Error(`调用失败：${response.status} ${detail}`);
    }
    const json = (await response.json()) as { content?: string };
    llmResult.value = json.content ?? "模型未返回内容。";
  } catch (error) {
    llmResult.value =
      error instanceof Error
        ? `${error.message}。请确认 python patch_service.py 正在运行。`
        : "调用失败，请确认 python patch_service.py 正在运行。";
  } finally {
    llmLoading.value = false;
  }
}

loadFromLocalStorage();
</script>

<template>
  <el-tabs v-model="appTab" type="border-card">
    <el-tab-pane label="核查运行台" name="workbench">
      <div class="tool-row">
        <el-button @click="saveToLocalStorage">保存配置到本地</el-button>
        <el-button @click="loadFromLocalStorage">从本地加载</el-button>
        <el-button @click="resetToDefaults">恢复默认</el-button>
        <el-button @click="exportConfigJson">导出JSON</el-button>
        <el-button @click="triggerImportJson">导入JSON</el-button>
      </div>
      <input
        ref="importInputRef"
        class="hidden-input"
        type="file"
        accept="application/json"
        @change="onImportFileChange"
      />
      <el-alert
        v-if="importError"
        title="导入失败"
        :description="importError"
        type="error"
        :closable="false"
      />
      <div class="config-workbench">
        <aside class="category-side">
          <p class="panel-title">核查工具箱</p>
          <el-menu :default-active="activeCategoryKey" class="category-menu" @select="(key: string) => (activeCategoryKey = key)">
            <el-menu-item v-for="category in normalizedCategories" :key="category.key" :index="category.key">
              {{ category.label }}
            </el-menu-item>
          </el-menu>
        </aside>

        <section class="scene-main" v-if="activeCategory">
          <div class="scene-header">
            <h3>{{ activeCategory.label }}</h3>
            <div class="scene-count-card">
              <span class="scene-count-label">场景总数</span>
              <strong class="scene-count-value">共 {{ activeCategoryScenes.length }} 个</strong>
            </div>
          </div>
          <el-select v-model="activeSerialNo" filterable placeholder="切换业务流水号">
            <el-option v-for="item in customerCases" :key="item.serialNo" :label="`${item.serialNo} - ${item.customerName}`" :value="item.serialNo" />
          </el-select>
          <el-alert :closable="false" type="warning" show-icon>
            <template #title>
              必须核查项：{{ activeMustCheck.map((item) => item.id).join("、") || "无" }}
            </template>
          </el-alert>
          <el-select
            v-model="activeCustomerRuleIds"
            multiple
            filterable
            collapse-tags
            collapse-tags-tooltip
            placeholder="设置该客户命中的规则（自动反推 mustCheckIds）"
          >
            <el-option
              v-for="rule in ruleBindings"
              :key="rule.id"
              :label="rule.ruleName"
              :value="rule.id"
            />
          </el-select>
          <div v-if="!isCustomCategory" class="scene-group">
            <p class="group-title">自动必选</p>
            <el-checkbox-group :model-value="activeRequiredScenes.map((item) => item.id)">
              <el-checkbox v-for="scene in activeRequiredScenes" :key="scene.id" :value="scene.id" disabled>
                {{ scene.sceneName }}：{{ scene.nlDescription }}
              </el-checkbox>
            </el-checkbox-group>
            <el-empty v-if="activeRequiredScenes.length === 0" description="当前大类无默认必选场景" :image-size="64" />
          </div>
          <div v-if="!isCustomCategory" class="scene-group">
            <p class="group-title">可选补充</p>
            <el-checkbox-group v-model="optionalSelection[activeCategory.key]">
              <el-checkbox v-for="scene in activeOptionalScenes" :key="scene.id" :value="scene.id">
                {{ scene.sceneName }}：{{ scene.nlDescription }}
              </el-checkbox>
            </el-checkbox-group>
          </div>
          <el-alert
            v-if="isCustomCategory"
            :closable="false"
            type="info"
            title="自定义核查说明"
            description="该分类仅支持自然语言提问，不配置固定场景。请输入你希望模型核查的问题并直接发起。"
          />
          <div v-if="isIntelligenceCategory" class="scene-editor">
            <h4>情报核查（行外邮箱协作）</h4>
            <el-input v-model="intelligenceMailbox" placeholder="指定行外邮箱地址" />
            <el-input
              v-model="intelligenceQuestion"
              type="textarea"
              :rows="3"
              placeholder="输入你想了解的客户外部信息，例如：近30天是否有新增负面舆情"
            />
            <el-button type="warning" @click="sendIntelligenceRequest">发送情报请求到邮箱</el-button>
            <el-table :data="intelligenceRequests" size="small" class="wrap-table">
              <el-table-column prop="serialNo" label="流水号" min-width="120" />
              <el-table-column prop="mailbox" label="目标邮箱" min-width="220" />
              <el-table-column prop="question" label="请求内容" min-width="220" />
              <el-table-column label="状态" min-width="100">
                <template #default="{ row }">
                  <el-tag :type="row.status === 'done' ? 'success' : 'warning'">
                    {{ row.status === "done" ? "已回传" : "处理中" }}
                  </el-tag>
                </template>
              </el-table-column>
              <el-table-column prop="result" label="返回结果" min-width="260" />
            </el-table>
          </div>
          <div class="query-bar">
            <el-input v-model="queryText" :placeholder="component.props.queryPlaceholder ?? '输入自然语言查询'" clearable />
            <el-button type="primary" :loading="runtime.isDispatching" @click="onStartAudit">
              {{ component.props.startButtonText ?? "开始智能核查" }}
            </el-button>
          </div>
          <el-select v-model="selectedSceneIdForJudge" filterable placeholder="选择需要大模型判定的场景">
            <el-option v-for="scene in sceneOptions" :key="scene.id" :label="scene.label" :value="scene.id" />
          </el-select>
          <el-input v-model="openAiKey" show-password placeholder="可选：输入 OpenAI Key 进行真实解读" />
          <el-input v-model="llmPrompt" type="textarea" :rows="3" placeholder="输入你想让模型解读的问题" />
          <el-button type="success" :loading="llmLoading" @click="runLlm">大模型场景判定与小结</el-button>
          <el-input v-model="llmResult" type="textarea" :rows="6" readonly placeholder="模型输出会显示在这里" />
        </section>
      </div>
    </el-tab-pane>

    <el-tab-pane label="场景配置" name="scenario">
      <div class="tool-row">
        <el-button type="primary" @click="addScenario">新增核查场景</el-button>
        <el-select v-model="editingSceneId" filterable placeholder="选择要编辑的场景">
          <el-option v-for="scene in sceneOptions" :key="scene.id" :label="scene.label" :value="scene.id" />
        </el-select>
      </div>
      <el-table :data="scenarioCatalog" size="small" class="wrap-table">
        <el-table-column prop="id" label="场景ID" min-width="150" />
        <el-table-column label="大类" min-width="120">
          <template #default="{ row }">{{ categoryLabelMap[row.categoryKey] }}</template>
        </el-table-column>
        <el-table-column prop="sceneName" label="场景名称" min-width="150" />
        <el-table-column prop="nlDescription" label="自然语言描述" min-width="260" />
        <el-table-column label="DSL特征数" min-width="100">
          <template #default="{ row }">{{ row.dslFeatures.length }}</template>
        </el-table-column>
        <el-table-column label="默认必查" min-width="100">
          <template #default="{ row }">
            <el-tag :type="row.requiredByDefault ? 'danger' : 'info'">
              {{ row.requiredByDefault ? "是" : "否" }}
            </el-tag>
          </template>
        </el-table-column>
      </el-table>
      <div class="scene-editor" v-if="editingScene">
        <h4>编辑场景：{{ editingScene.sceneName }}</h4>
        <el-form label-width="120px">
          <el-form-item label="场景分类">
            <el-select v-model="editingScene.categoryKey">
              <el-option
                v-for="category in configurableCategories"
                :key="category.key"
                :label="category.label"
                :value="category.key"
              />
            </el-select>
          </el-form-item>
          <el-form-item label="场景名称">
            <el-input v-model="editingScene.sceneName" />
          </el-form-item>
          <el-form-item label="自然语言描述">
            <el-input v-model="editingScene.nlDescription" type="textarea" :rows="3" />
          </el-form-item>
          <el-form-item label="默认必查">
            <el-switch v-model="editingScene.requiredByDefault" />
          </el-form-item>
          <el-form-item label="DSL特征(JSON)">
            <el-input v-model="editingFeaturesText" type="textarea" :rows="8" />
          </el-form-item>
          <el-form-item>
            <el-button type="primary" @click="applySceneFeatureJson">应用DSL特征配置</el-button>
          </el-form-item>
        </el-form>
      </div>
    </el-tab-pane>

    <el-tab-pane label="规则绑定" name="binding">
      <div class="tool-row binding-row">
        <el-input v-model="newRuleName" placeholder="规则中文名称，例如：设备异常联动规则" />
        <el-select v-model="selectedScenarioIds" multiple filterable collapse-tags placeholder="选择绑定场景（按大类小场景）">
          <el-option
            v-for="item in sceneOptions"
            :key="item.id"
            :label="item.label"
            :value="item.id"
          />
        </el-select>
        <el-button type="primary" @click="addRuleBinding">新增绑定</el-button>
      </div>
      <el-table :data="ruleBindings" size="small" class="wrap-table">
        <el-table-column prop="id" label="规则ID" min-width="180" />
        <el-table-column prop="ruleName" label="规则名称" min-width="200" />
        <el-table-column label="绑定场景" min-width="420">
          <template #default="{ row }">
            <el-tag v-for="id in row.scenarioIds" :key="`${row.id}_${id}`" class="scenario-tag">
              {{ sceneOptions.find((item) => item.id === id)?.label ?? id }}
            </el-tag>
          </template>
        </el-table-column>
      </el-table>
    </el-tab-pane>
  </el-tabs>
</template>

<style scoped>
.config-workbench { display: grid; grid-template-columns: 240px minmax(0, 1fr); gap: 16px; }
.category-side { border: 1px solid #dce6f3; border-radius: 16px; background: #f8fbff; padding: 12px; }
.panel-title { margin: 0 0 10px; font-size: 14px; font-weight: 700; color: #34495e; }
.category-menu { border-right: none; background: transparent; }
.scene-main { border: 1px solid #dce6f3; border-radius: 16px; background: #fff; padding: 16px; display: grid; gap: 12px; }
.scene-header {
  display: flex;
  justify-content: space-between;
  align-items: flex-start;
  gap: 10px;
  flex-wrap: wrap;
}
.scene-header h3 { margin: 0; font-size: 18px; }
.scene-count-card {
  min-width: 112px;
  padding: 8px 10px;
  border: 1px solid #cfdff7;
  border-radius: 10px;
  background: linear-gradient(180deg, #f6faff 0%, #ecf4ff 100%);
  display: grid;
  gap: 2px;
  text-align: right;
}
.scene-count-label {
  font-size: 12px;
  line-height: 1.2;
  color: #52606d;
}
.scene-count-value {
  font-size: 14px;
  line-height: 1.25;
  color: #175cd3;
}
.group-title { margin: 0 0 8px; font-weight: 700; color: #52606d; }
.scene-group :deep(.el-checkbox) { display: flex; margin-bottom: 10px; line-height: 1.6; }
.query-bar { display: grid; grid-template-columns: 1fr auto; gap: 12px; }
.tool-row { margin-bottom: 12px; display: flex; gap: 10px; flex-wrap: wrap; }
.binding-row { display: grid; grid-template-columns: 1fr 1.4fr auto; }
.scenario-tag { margin-right: 6px; margin-bottom: 6px; }
.scene-editor { margin-top: 16px; border: 1px solid #dce6f3; border-radius: 12px; padding: 14px; background: #fff; }
.hidden-input { display: none; }
.wrap-table :deep(.cell) {
  white-space: normal;
  word-break: break-word;
  line-height: 1.5;
}
.scene-main :deep(.el-tag),
.scene-main :deep(.el-alert__title),
.scene-main :deep(.el-alert__description) {
  white-space: normal;
  word-break: break-word;
}
@media (max-width: 980px) {
  .config-workbench { grid-template-columns: 1fr; }
  .query-bar, .binding-row { grid-template-columns: 1fr; }
}
</style>
