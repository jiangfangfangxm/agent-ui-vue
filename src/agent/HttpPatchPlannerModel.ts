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
    let response: Response;

    try {
      response = await fetch(this.endpoint, {
        method: "POST",
        headers: {
          "Content-Type": "application/json",
        },
        body: JSON.stringify(input),
      });
    } catch (error) {
      throw new Error(
        "无法连接 Python Patch 服务。请先在 python 目录运行 python patch_service.py，并确认 http://127.0.0.1:8000/health 可访问。",
      );
    }

    if (!response.ok) {
      const errorText = await response.text();
      throw new Error(
        `Python Patch 服务调用失败：${response.status} ${response.statusText}${errorText ? ` - ${errorText}` : ""}。请确认 python patch_service.py 正在 127.0.0.1:8000 运行。`,
      );
    }

    return (await response.json()) as PatchPlanningOutput;
  }
}
