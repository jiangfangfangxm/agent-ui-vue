import type { PatchPlannerModel } from "./PatchPlannerAgent";
import type { PatchPlanningInput, PatchPlanningOutput } from "./contracts";

/**
 * 通过本地 HTTP API 调用 Python patch 服务。
 * 前端只负责把当前 envelope 和 event 发给服务端，
 * 由服务端决定返回哪些 patch。
 */
export class HttpPatchPlannerModel implements PatchPlannerModel {
  constructor(private readonly endpoint = "/api/patch-plan") {}

  async generate(input: PatchPlanningInput): Promise<PatchPlanningOutput> {
    const response = await fetch(this.endpoint, {
      method: "POST",
      headers: {
        "Content-Type": "application/json",
      },
      body: JSON.stringify(input),
    });

    if (!response.ok) {
      const errorText = await response.text();
      throw new Error(
        `Python Patch 服务调用失败：${response.status} ${response.statusText}${errorText ? ` - ${errorText}` : ""}`,
      );
    }

    return (await response.json()) as PatchPlanningOutput;
  }
}
