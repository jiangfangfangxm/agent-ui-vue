# Python Patch Builders

这是一套给 Python Agent 使用的 patch-builder 模块。  
它的目标是把“业务意图 / 业务数据 -> PatchOperation[]”这件事收敛成可控、可测试的 Python 函数。

## 目录

```text
python/
  agent_patch_builders/
    __init__.py
    models.py
    patch_helpers.py
    message_builders.py
    section_builders.py
    summary_builders.py
    patch_engine.py
    workflow_action_builders.py
  tests/
    test_patch_builders.py
```

## 当前提供的函数

- `build_init_event_patches(...)`
- `build_toggle_checklist_item_patches(...)`
- `build_add_checklist_item_patches(...)`
- `build_risk_check_event_patches(...)`
- `build_open_detail_patches(...)`
- `apply_patches(...)`

## 适用场景

适合让 Python 侧的 Agent：

1. 读取当前 `WorkflowEnvelope`
2. 结合业务数据决定动作
3. 调用 builder 生成 patch
4. 在本地测试 patch 是否符合预期

## 示例

```python
from agent_patch_builders.workflow_action_builders import build_init_event_patches

patches = build_init_event_patches(
    envelope=current_envelope,
    event={
        "id": "evt_init_1",
        "type": "init_event",
        "componentId": "system_init",
        "timestamp": "09:30",
        "payload": {},
    },
)
```

## 运行测试

在仓库根目录执行：

```powershell
cd C:\Users\PC\Documents\Codex\2026-04-24\github\agent-ui-vue\python
python -m unittest discover -s tests -p "test_*.py"
```

## 设计原则

- 纯 Python
- 零第三方依赖
- 输入是业务数据和 envelope
- 输出是标准 patch 字典
- 可以本地单测
- 便于后续对接真实 Python Agent
