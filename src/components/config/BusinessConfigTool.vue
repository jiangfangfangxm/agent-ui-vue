<script setup lang="ts">
import { computed, reactive, ref } from "vue";
import { appConfig, type GeneratedAppConfig } from "../../workflow/appConfig";

type EditableConfig = GeneratedAppConfig & {
  schemaVersion?: string;
  compiler?: {
    targets?: Record<string, Record<string, string>>;
    generationPolicy?: {
      overwriteManualFiles?: boolean;
      generatedDirectory?: string;
      requireContractTests?: boolean;
      requireIllegalEventTests?: boolean;
    };
  };
  testContracts?: {
    requiredPaths?: unknown[];
    illegalEvents?: unknown[];
  };
  modes?: Record<string, { allowedEvents?: string[]; title?: string; baseState?: string }>;
  sections: Record<
    string,
    {
      title?: string;
      builder?: string;
      source?: string;
      contextBinding?: string;
      contextBindings?: string[];
      components?: Array<{
        id: string;
        type: string;
        eventType?: string;
        actions?: Array<{ label: string; eventType: string; buttonType?: string }>;
      }>;
    }
  >;
};

interface ValidationIssue {
  type: "error" | "warning";
  scope: string;
  message: string;
}

function clone<T>(value: T): T {
  return JSON.parse(JSON.stringify(value)) as T;
}

const draft = reactive(clone(appConfig) as EditableConfig);
const selectedState = ref(Object.keys(draft.states)[0] ?? "");
const selectedEvent = ref(Object.keys(draft.events)[0] ?? "");
const selectedSection = ref(Object.keys(draft.sections)[0] ?? "");
const dslFilePath = ref("apps/warning-review.app.yaml");

const stateOptions = computed(() => Object.keys(draft.states));
const eventOptions = computed(() => Object.keys(draft.events));
const sectionOptions = computed(() => Object.keys(draft.sections));
const contextOptions = computed(() => Object.keys(draft.context));

const activeState = computed(() => draft.states[selectedState.value]);
const activeEvent = computed(() => draft.events[selectedEvent.value]);
const activeSection = computed(() => draft.sections[selectedSection.value]);
const activeEventTransition = computed(() => {
  if (!activeEvent.value) {
    return {};
  }

  activeEvent.value.transition ??= {};
  return activeEvent.value.transition;
});

const validationIssues = computed<ValidationIssue[]>(() => {
  const issues: ValidationIssue[] = [];
  const states = new Set(Object.keys(draft.states));
  const events = new Set(Object.keys(draft.events));
  const sections = new Set(Object.keys(draft.sections));
  const contextFields = new Set(Object.keys(draft.context));

  if (!states.has(draft.app.entryState)) {
    issues.push({
      type: "error",
      scope: "app.entryState",
      message: `入口状态不存在：${draft.app.entryState}`,
    });
  }

  if (!events.has(draft.app.initialEvent)) {
    issues.push({
      type: "error",
      scope: "app.initialEvent",
      message: `初始化事件不存在：${draft.app.initialEvent}`,
    });
  }

  for (const [stateId, state] of Object.entries(draft.states)) {
    for (const eventType of state.allowedEvents ?? []) {
      if (!events.has(eventType)) {
        issues.push({
          type: "error",
          scope: `state.${stateId}`,
          message: `allowedEvents 引用了未知事件：${eventType}`,
        });
      }
    }

    for (const sectionId of state.visibleSections ?? []) {
      if (!sections.has(sectionId)) {
        issues.push({
          type: "error",
          scope: `state.${stateId}`,
          message: `visibleSections 引用了未知 section：${sectionId}`,
        });
      }
    }
  }

  for (const [eventType, event] of Object.entries(draft.events)) {
    for (const stateId of event.allowedStates ?? []) {
      if (!states.has(stateId) && stateId !== "presenting_result") {
        issues.push({
          type: "error",
          scope: `event.${eventType}`,
          message: `allowedStates 引用了未知状态：${stateId}`,
        });
      }
    }

    for (const field of event.transition?.contextWrites ?? []) {
      if (!contextFields.has(field)) {
        issues.push({
          type: "error",
          scope: `event.${eventType}`,
          message: `contextWrites 引用了未知 context 字段：${field}`,
        });
      }
    }
  }

  for (const [sectionId, section] of Object.entries(draft.sections)) {
    if (section.contextBinding && !contextFields.has(section.contextBinding)) {
      issues.push({
        type: "error",
        scope: `section.${sectionId}`,
        message: `contextBinding 引用了未知 context 字段：${section.contextBinding}`,
      });
    }

    for (const field of section.contextBindings ?? []) {
      if (!contextFields.has(field)) {
        issues.push({
          type: "error",
          scope: `section.${sectionId}`,
          message: `contextBindings 引用了未知 context 字段：${field}`,
        });
      }
    }
  }

  if (!issues.length) {
    issues.push({
      type: "warning",
      scope: "config",
      message: "当前配置未发现阻断性问题",
    });
  }

  return issues;
});

const errorCount = computed(
  () => validationIssues.value.filter((issue) => issue.type === "error").length,
);

function normalizeListText(value: string): string[] {
  return value
    .split("\n")
    .map((item) => item.trim())
    .filter(Boolean);
}

function listText(value?: string[]): string {
  return (value ?? []).join("\n");
}

function updateStateAllowedEvents(value: string): void {
  if (!activeState.value) return;
  activeState.value.allowedEvents = normalizeListText(value);
}

function updateStateVisibleSections(value: string): void {
  if (!activeState.value) return;
  activeState.value.visibleSections = normalizeListText(value);
}

function updateEventAllowedStates(value: string): void {
  if (!activeEvent.value) return;
  activeEvent.value.allowedStates = normalizeListText(value);
}

function updateSectionContextBindings(value: string): void {
  if (!activeSection.value) return;
  activeSection.value.contextBindings = normalizeListText(value);
}

function addState(): void {
  const id = `state_${Object.keys(draft.states).length + 1}`;
  draft.states[id] = {
    title: "新阶段",
    description: "",
    allowedEvents: ["open_detail"],
    visibleSections: [],
  };
  selectedState.value = id;
}

function addEvent(): void {
  const id = `event_${Object.keys(draft.events).length + 1}`;
  draft.events[id] = {
    allowedStates: [draft.app.entryState],
    payloadSchema: {
      type: "object",
      required: [],
      properties: {},
    },
  };
  selectedEvent.value = id;
}

function addSection(): void {
  const id = `sec_custom_${Object.keys(draft.sections).length + 1}`;
  draft.sections[id] = {
    title: "新区块",
    components: [],
  };
  selectedSection.value = id;
}

function toYaml(value: unknown, indent = 0): string {
  const space = " ".repeat(indent);

  if (Array.isArray(value)) {
    if (!value.length) return "[]";
    return value
      .map((item) => {
        if (typeof item === "object" && item !== null) {
          return `${space}- ${toYaml(item, indent + 2).trimStart()}`;
        }
        return `${space}- ${formatScalar(item)}`;
      })
      .join("\n");
  }

  if (typeof value === "object" && value !== null) {
    const entries = Object.entries(value as Record<string, unknown>);
    if (!entries.length) return "{}";
    return entries
      .map(([key, item]) => {
        if (typeof item === "object" && item !== null) {
          const rendered = toYaml(item, indent + 2);
          return `${space}${key}: ${rendered === "[]" || rendered === "{}" ? rendered : `\n${rendered}`}`;
        }
        return `${space}${key}: ${formatScalar(item)}`;
      })
      .join("\n");
  }

  return `${space}${formatScalar(value)}`;
}

function formatScalar(value: unknown): string {
  if (value === null || value === undefined) return "null";
  if (typeof value === "boolean" || typeof value === "number") return String(value);
  const text = String(value);
  if (!text) return '""';
  if (/[:#\n]|^\s|\s$/.test(text)) return JSON.stringify(text);
  return text;
}

const exportedYaml = computed(() => toYaml(draft));
const compileCommand = computed(
  () => `python tools/app_compiler.py ${dslFilePath.value}`,
);
const generatedDirectory = computed(
  () => draft.compiler?.generationPolicy?.generatedDirectory ?? "generated",
);
const normalizedOutputPath = computed(
  () => `${generatedDirectory.value}/${draft.app.id}/app.normalized.json`,
);
const compileArtifacts = computed(() => {
  const artifacts = [
    {
      category: "normalized",
      name: "运行时配置",
      path: normalizedOutputPath.value,
      description: "前端 Runtime 与 Python patch service 共同加载的规范化配置。",
    },
    {
      category: "frontend",
      name: "前端事件契约",
      path: `${generatedDirectory.value}/${draft.app.id}/frontend/workflow-definition.generated.ts`,
      description: "用于对照前端 WorkflowEvent、allowedEvents 与 payload schema。",
    },
    {
      category: "python",
      name: "Python 事件契约",
      path: `${generatedDirectory.value}/${draft.app.id}/python/workflow_definition.generated.py`,
      description: "用于对照 Python patch builders 的阶段流转契约。",
    },
    {
      category: "tests",
      name: "阶段流转契约测试",
      path: `${generatedDirectory.value}/${draft.app.id}/tests/test_transition_contracts.generated.py`,
      description: "根据 DSL testContracts 生成的回归测试骨架。",
    },
    {
      category: "docs",
      name: "生成说明",
      path: `${generatedDirectory.value}/${draft.app.id}/README.generated.md`,
      description: "记录本次编译产物和后续接入边界。",
    },
  ];

  const targets = draft.compiler?.targets ?? {};
  for (const [category, entries] of Object.entries(targets)) {
    for (const [name, path] of Object.entries(entries)) {
      artifacts.push({
        category,
        name,
        path,
        description: "DSL 声明的人工维护目标文件；当前编译策略不会自动覆盖。",
      });
    }
  }

  return artifacts;
});
const compileChecks = computed(() => [
  {
    name: "引用校验",
    status: errorCount.value ? "error" : "success",
    message: errorCount.value
      ? `存在 ${errorCount.value} 个阻断性配置错误，需修复后再编译。`
      : "状态、事件、区块和 context 引用未发现阻断性问题。",
  },
  {
    name: "契约测试",
    status: draft.compiler?.generationPolicy?.requireContractTests ? "success" : "warning",
    message: draft.compiler?.generationPolicy?.requireContractTests
      ? `已声明 ${draft.testContracts?.requiredPaths?.length ?? 0} 条必达路径契约。`
      : "建议启用 compiler.generationPolicy.requireContractTests。",
  },
  {
    name: "非法事件测试",
    status: draft.compiler?.generationPolicy?.requireIllegalEventTests ? "success" : "warning",
    message: draft.compiler?.generationPolicy?.requireIllegalEventTests
      ? `已声明 ${draft.testContracts?.illegalEvents?.length ?? 0} 条非法事件契约。`
      : "建议启用 compiler.generationPolicy.requireIllegalEventTests。",
  },
  {
    name: "人工文件保护",
    status: draft.compiler?.generationPolicy?.overwriteManualFiles ? "warning" : "success",
    message: draft.compiler?.generationPolicy?.overwriteManualFiles
      ? "当前策略允许覆盖人工维护文件，编译前需谨慎确认。"
      : "当前策略不会自动覆盖 src 与 python 下的人工维护文件。",
  },
]);
const canCompile = computed(() => errorCount.value === 0);
</script>

<template>
  <div class="config-tool">
    <header class="config-header">
      <div>
        <p class="eyebrow">应用配置工具</p>
        <h1>{{ draft.app.name }}</h1>
        <p class="subtitle">{{ draft.app.description }}</p>
      </div>
      <div class="summary-grid">
        <el-statistic title="状态" :value="stateOptions.length" />
        <el-statistic title="事件" :value="eventOptions.length" />
        <el-statistic title="区块" :value="sectionOptions.length" />
        <el-tag :type="errorCount ? 'danger' : 'success'" size="large">
          {{ errorCount ? `${errorCount} 个错误` : "校验通过" }}
        </el-tag>
      </div>
    </header>

    <el-tabs class="config-tabs" type="border-card">
      <el-tab-pane label="应用">
        <section class="panel-grid two">
          <el-card shadow="never">
            <template #header>基本信息</template>
            <div class="form-grid">
              <label>
                <span>应用 ID</span>
                <el-input v-model="draft.app.id" />
              </label>
              <label>
                <span>应用名称</span>
                <el-input v-model="draft.app.name" />
              </label>
              <label>
                <span>入口状态</span>
                <el-select v-model="draft.app.entryState" filterable>
                  <el-option
                    v-for="stateId in stateOptions"
                    :key="stateId"
                    :label="stateId"
                    :value="stateId"
                  />
                </el-select>
              </label>
              <label>
                <span>初始化事件</span>
                <el-select v-model="draft.app.initialEvent" filterable>
                  <el-option
                    v-for="eventType in eventOptions"
                    :key="eventType"
                    :label="eventType"
                    :value="eventType"
                  />
                </el-select>
              </label>
              <label class="wide">
                <span>描述</span>
                <el-input v-model="draft.app.description" type="textarea" :rows="4" />
              </label>
            </div>
          </el-card>

          <el-card shadow="never">
            <template #header>业务上下文</template>
            <el-table :data="contextOptions.map((name) => ({ name, ...draft.context[name] }))" size="small">
              <el-table-column prop="name" label="字段" min-width="160" />
              <el-table-column prop="type" label="类型" min-width="140" />
              <el-table-column prop="description" label="说明" min-width="240" />
            </el-table>
          </el-card>
        </section>
      </el-tab-pane>

      <el-tab-pane label="阶段">
        <section class="editor-layout">
          <aside class="selector-panel">
            <div class="panel-head">
              <strong>阶段</strong>
              <el-button size="small" @click="addState">新增</el-button>
            </div>
            <el-menu class="selector-menu" :default-active="selectedState" @select="selectedState = String($event)">
              <el-menu-item v-for="stateId in stateOptions" :key="stateId" :index="stateId">
                {{ stateId }}
              </el-menu-item>
            </el-menu>
          </aside>

          <el-card v-if="activeState" class="editor-card" shadow="never">
            <template #header>{{ selectedState }}</template>
            <div class="form-grid">
              <label>
                <span>标题</span>
                <el-input v-model="activeState.title" />
              </label>
              <label>
                <span>分类</span>
                <el-input v-model="activeState.category" />
              </label>
              <label class="wide">
                <span>说明</span>
                <el-input v-model="activeState.description" type="textarea" :rows="3" />
              </label>
              <label>
                <span>允许事件</span>
                <el-input
                  :model-value="listText(activeState.allowedEvents)"
                  type="textarea"
                  :rows="8"
                  @update:model-value="updateStateAllowedEvents"
                />
              </label>
              <label>
                <span>可见区块</span>
                <el-input
                  :model-value="listText(activeState.visibleSections)"
                  type="textarea"
                  :rows="8"
                  @update:model-value="updateStateVisibleSections"
                />
              </label>
            </div>
          </el-card>
        </section>
      </el-tab-pane>

      <el-tab-pane label="事件">
        <section class="editor-layout">
          <aside class="selector-panel">
            <div class="panel-head">
              <strong>事件</strong>
              <el-button size="small" @click="addEvent">新增</el-button>
            </div>
            <el-menu class="selector-menu" :default-active="selectedEvent" @select="selectedEvent = String($event)">
              <el-menu-item v-for="eventType in eventOptions" :key="eventType" :index="eventType">
                {{ eventType }}
              </el-menu-item>
            </el-menu>
          </aside>

          <el-card v-if="activeEvent" class="editor-card" shadow="never">
            <template #header>{{ selectedEvent }}</template>
            <div class="form-grid">
              <label>
                <span>标签</span>
                <el-input v-model="activeEvent.label" />
              </label>
              <label>
                <span>处理程序</span>
                <el-input v-model="activeEvent.handler" />
              </label>
              <label>
                <span>来源</span>
                <el-input v-model="activeEvent.source" />
              </label>
              <label>
                <span>目标状态</span>
                <el-input v-model="activeEventTransition.toState" />
              </label>
              <label>
                <span>允许状态</span>
                <el-input
                  :model-value="listText(activeEvent.allowedStates)"
                  type="textarea"
                  :rows="6"
                  @update:model-value="updateEventAllowedStates"
                />
              </label>
              <label>
                <span>Payload Schema</span>
                <el-input
                  :model-value="JSON.stringify(activeEvent.payloadSchema ?? {}, null, 2)"
                  type="textarea"
                  :rows="10"
                  readonly
                />
              </label>
            </div>
          </el-card>
        </section>
      </el-tab-pane>

      <el-tab-pane label="区块">
        <section class="editor-layout">
          <aside class="selector-panel">
            <div class="panel-head">
              <strong>区块</strong>
              <el-button size="small" @click="addSection">新增</el-button>
            </div>
            <el-menu class="selector-menu" :default-active="selectedSection" @select="selectedSection = String($event)">
              <el-menu-item v-for="sectionId in sectionOptions" :key="sectionId" :index="sectionId">
                {{ sectionId }}
              </el-menu-item>
            </el-menu>
          </aside>

          <el-card v-if="activeSection" class="editor-card" shadow="never">
            <template #header>{{ selectedSection }}</template>
            <div class="form-grid">
              <label>
                <span>标题</span>
                <el-input v-model="activeSection.title" />
              </label>
              <label>
                <span>Builder</span>
                <el-input v-model="activeSection.builder" />
              </label>
              <label>
                <span>Context Binding</span>
                <el-select v-model="activeSection.contextBinding" filterable clearable>
                  <el-option
                    v-for="field in contextOptions"
                    :key="field"
                    :label="field"
                    :value="field"
                  />
                </el-select>
              </label>
              <label>
                <span>Context Bindings</span>
                <el-input
                  :model-value="listText(activeSection.contextBindings)"
                  type="textarea"
                  :rows="6"
                  @update:model-value="updateSectionContextBindings"
                />
              </label>
              <label class="wide">
                <span>组件</span>
                <el-table :data="activeSection.components ?? []" size="small">
                  <el-table-column prop="id" label="ID" min-width="180" />
                  <el-table-column prop="type" label="类型" min-width="120" />
                  <el-table-column prop="eventType" label="事件" min-width="180" />
                </el-table>
              </label>
            </div>
          </el-card>
        </section>
      </el-tab-pane>

      <el-tab-pane label="校验">
        <el-table :data="validationIssues" size="small">
          <el-table-column label="级别" width="100">
            <template #default="{ row }">
              <el-tag :type="row.type === 'error' ? 'danger' : 'success'" size="small">
                {{ row.type }}
              </el-tag>
            </template>
          </el-table-column>
          <el-table-column prop="scope" label="范围" min-width="220" />
          <el-table-column prop="message" label="消息" min-width="360" />
        </el-table>
      </el-tab-pane>

      <el-tab-pane label="编译">
        <section class="panel-grid two">
          <el-card shadow="never">
            <template #header>编译状态</template>
            <div class="compile-status">
              <el-alert
                :title="canCompile ? '当前配置可以进入 CLI 编译' : '当前配置存在阻断性错误'"
                :type="canCompile ? 'success' : 'error'"
                :closable="false"
                show-icon
              />
              <el-table :data="compileChecks" size="small">
                <el-table-column label="状态" width="96">
                  <template #default="{ row }">
                    <el-tag :type="row.status === 'error' ? 'danger' : row.status" size="small">
                      {{ row.status }}
                    </el-tag>
                  </template>
                </el-table-column>
                <el-table-column prop="name" label="检查项" min-width="140" />
                <el-table-column prop="message" label="说明" min-width="320" />
              </el-table>
            </div>
          </el-card>

          <el-card shadow="never">
            <template #header>CLI 编译命令</template>
            <div class="command-panel">
              <p>将“导出”页内容写入 DSL 文件后，在项目根目录执行：</p>
              <label>
                <span>DSL 文件路径</span>
                <el-input v-model="dslFilePath" />
              </label>
              <el-input class="command-box" :model-value="compileCommand" readonly />
              <p class="hint">
                浏览器配置工具当前只生成配置和命令，不直接写文件或执行本地 Python。
              </p>
              <el-descriptions :column="1" border size="small">
                <el-descriptions-item label="输入 DSL">
                  {{ dslFilePath }}
                </el-descriptions-item>
                <el-descriptions-item label="规范化配置">
                  {{ normalizedOutputPath }}
                </el-descriptions-item>
                <el-descriptions-item label="生成目录">
                  {{ generatedDirectory }}
                </el-descriptions-item>
              </el-descriptions>
            </div>
          </el-card>
        </section>

        <el-card class="artifact-card" shadow="never">
          <template #header>预计产物</template>
          <el-table :data="compileArtifacts" size="small">
            <el-table-column prop="category" label="类别" width="120" />
            <el-table-column prop="name" label="名称" min-width="170" />
            <el-table-column prop="path" label="路径" min-width="340" />
            <el-table-column prop="description" label="说明" min-width="360" />
          </el-table>
        </el-card>
      </el-tab-pane>

      <el-tab-pane label="导出">
        <el-input class="export-box" :model-value="exportedYaml" type="textarea" :rows="28" readonly />
      </el-tab-pane>
    </el-tabs>
  </div>
</template>

<style scoped>
.config-tool {
  min-height: 100vh;
  padding: 24px;
}

.config-header {
  display: flex;
  justify-content: space-between;
  gap: 24px;
  align-items: center;
  margin-bottom: 20px;
  padding: 22px 24px;
  border: 1px solid #dbe4ef;
  border-radius: 8px;
  background: #ffffff;
  box-shadow: 0 10px 28px rgb(15 23 42 / 0.08);
}

.eyebrow {
  margin: 0 0 6px;
  font-size: 12px;
  font-weight: 700;
  color: #52606d;
}

h1 {
  margin: 0;
  font-size: 26px;
}

.subtitle {
  margin: 8px 0 0;
  color: #52606d;
}

.summary-grid {
  display: grid;
  grid-template-columns: repeat(4, auto);
  gap: 18px;
  align-items: center;
}

.config-tabs {
  border-radius: 8px;
  overflow: hidden;
}

.panel-grid {
  display: grid;
  gap: 16px;
}

.panel-grid.two {
  grid-template-columns: minmax(0, 1fr) minmax(0, 1.2fr);
}

.editor-layout {
  display: grid;
  grid-template-columns: 280px minmax(0, 1fr);
  gap: 16px;
}

.selector-panel,
.editor-card {
  min-width: 0;
}

.selector-panel {
  border: 1px solid #e1e8f0;
  border-radius: 8px;
  background: #fff;
  overflow: hidden;
}

.panel-head {
  display: flex;
  justify-content: space-between;
  align-items: center;
  padding: 12px;
  border-bottom: 1px solid #e1e8f0;
}

.selector-menu {
  border-right: 0;
  max-height: 620px;
  overflow: auto;
}

.form-grid {
  display: grid;
  grid-template-columns: repeat(2, minmax(0, 1fr));
  gap: 14px 16px;
}

label {
  display: grid;
  gap: 6px;
  min-width: 0;
  color: #334155;
  font-size: 13px;
  font-weight: 600;
}

label.wide {
  grid-column: 1 / -1;
}

.export-box {
  font-family: Consolas, "Courier New", monospace;
}

.compile-status,
.command-panel {
  display: grid;
  gap: 14px;
}

.command-panel p {
  margin: 0;
  color: #52606d;
  line-height: 1.6;
}

.command-box {
  font-family: Consolas, "Courier New", monospace;
}

.hint {
  font-size: 13px;
}

.artifact-card {
  margin-top: 16px;
}

@media (max-width: 980px) {
  .config-header,
  .editor-layout,
  .panel-grid.two,
  .form-grid {
    grid-template-columns: 1fr;
  }

  .config-header {
    display: grid;
  }

  .summary-grid {
    grid-template-columns: repeat(2, minmax(0, 1fr));
  }
}
</style>
