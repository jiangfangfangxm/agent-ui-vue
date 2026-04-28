/**
 * Patch Engine。
 * 这是 WorkflowEnvelope 的正式更新入口，用于把 PatchOperation[] 转成新的页面状态。
 * 如果需要新增 UI 变化能力，优先扩展这里的 patch 语义，而不是在组件层直接改状态。
 */
import type {
  PatchExecutionResult,
  PatchOperation,
  UISection,
  WorkflowEnvelope,
} from "../types/workflow";

export class PatchApplicationError extends Error {
  constructor(message: string, readonly patch: PatchOperation) {
    super(message);
    this.name = "PatchApplicationError";
  }
}

function dedupeEventTypes(events: string[]): string[] {
  return [...new Set(events)];
}

// 在执行替换、删除或定点插入前，先确认目标 section 已存在。
function ensureSectionExists(
  sections: UISection[],
  sectionId: string,
  patch: PatchOperation,
): void {
  if (!sections.some((section) => section.id === sectionId)) {
    throw new PatchApplicationError(
      `操作“${patch.op}”未找到目标分区“${sectionId}”。`,
      patch,
    );
  }
}

// 在执行追加类操作前，先防止生成重复的 section id。
function ensureSectionMissing(
  sections: UISection[],
  sectionId: string,
  patch: PatchOperation,
): void {
  if (sections.some((section) => section.id === sectionId)) {
    throw new PatchApplicationError(
      `分区“${sectionId}”已存在，操作“${patch.op}”会产生重复分区。`,
      patch,
    );
  }
}

// 单条 patch 的应用逻辑。这里负责把协议语义翻译成新的 envelope。
function applyPatch(
  envelope: WorkflowEnvelope,
  patch: PatchOperation,
): WorkflowEnvelope {
  const sections = envelope.page.sections;

  switch (patch.op) {
    case "set_state":
      return { ...envelope, state: patch.value };
    case "replace_section":
      ensureSectionExists(sections, patch.sectionId, patch);

      if (patch.value.id !== patch.sectionId) {
        throw new PatchApplicationError(
          `replace_section 要求 value.id 与 sectionId 保持一致（当前目标为“${patch.sectionId}”）。`,
          patch,
        );
      }

      return {
        ...envelope,
        page: {
          ...envelope.page,
          sections: sections.map((section) =>
            section.id === patch.sectionId ? patch.value : section,
          ),
        },
      };
    case "append_section":
      ensureSectionMissing(sections, patch.value.id, patch);

      if (patch.beforeSectionId) {
        ensureSectionExists(sections, patch.beforeSectionId, patch);

        const insertIndex = sections.findIndex(
          (section) => section.id === patch.beforeSectionId,
        );

        return {
          ...envelope,
          page: {
            ...envelope.page,
            sections: [
              ...sections.slice(0, insertIndex),
              patch.value,
              ...sections.slice(insertIndex),
            ],
          },
        };
      }

      return {
        ...envelope,
        page: {
          ...envelope.page,
          sections: [...sections, patch.value],
        },
      };
    case "remove_section":
      ensureSectionExists(sections, patch.sectionId, patch);

      return {
        ...envelope,
        page: {
          ...envelope.page,
          sections: sections.filter((section) => section.id !== patch.sectionId),
        },
      };
    case "prepend_message":
      return {
        ...envelope,
        messages: [patch.value, ...envelope.messages],
      };
    case "set_allowed_events":
      return { ...envelope, allowedEvents: dedupeEventTypes(patch.value) };
    case "set_risk_summary":
      return { ...envelope, riskSummary: patch.value };
    default:
      return envelope;
  }
}

// 顺序执行 patch 列表，并保留实际已应用的 patch 记录，便于运行时观测和调试。
export function applyPatches(
  envelope: WorkflowEnvelope,
  patches: PatchOperation[],
): PatchExecutionResult {
  return patches.reduce<PatchExecutionResult>(
    (current, patch) => ({
      envelope: applyPatch(current.envelope, patch),
      appliedPatches: [...current.appliedPatches, patch],
    }),
    {
      envelope,
      appliedPatches: [],
    },
  );
}
