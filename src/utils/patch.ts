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
