# 应用配置目录

本目录用于存放面向业务配置工具和后续编译/组装工具的应用配置文件。

当前示例：

- `warning-review.app.yaml`：预警核查工作台配置 DSL。

## 配置文件定位

`*.app.yaml` 是业务应用的中间表示，不直接由当前 runtime 加载。

它用于描述：

- 应用基本信息
- 业务 context
- 工作流阶段
- 阶段 allowedEvents
- 事件契约
- section 与 widget 绑定
- 初始业务数据
- 编译目标
- 测试契约

后续编译/组装工具可以基于该配置生成：

- 前端事件契约
- Python 事件契约
- 初始 envelope
- section builder 骨架
- patch builder 骨架
- 阶段流转契约测试
- 应用说明文档

## 编译命令

当前 CLI 编译器位于：

```text
tools/app_compiler.py
```

执行：

```bash
python tools/app_compiler.py apps/warning-review.app.yaml
```

默认输出到：

```text
generated/warning_review_workbench/
```

当前生成内容：

```text
app.normalized.json
frontend/workflow-definition.generated.ts
python/workflow_definition.generated.py
tests/test_transition_contracts.generated.py
README.generated.md
```

说明：

- 生成产物暂不自动接入 runtime。
- 编译器不会覆盖当前人工维护的 `src/` 或 `python/agent_patch_builders/` 文件。
- 下一阶段可以把 generated 文件逐步接入 runtime 或作为代码生成模板继续扩展。

## 当前约束

- 配置文件是“业务语义”的单一来源。
- 复杂业务逻辑不强行塞进 YAML，应通过 handler 或插件扩展。
- 编译器初期应生成到 `generated/` 目录，避免覆盖人工维护代码。
- 每个新增状态和事件都必须能生成对应的契约测试。
