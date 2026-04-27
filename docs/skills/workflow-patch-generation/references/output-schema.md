# 输出结构

返回 JSON：

```json
{
  "patches": [],
  "rationale": "",
  "warnings": []
}
```

## 字段说明

### patches

类型：

```ts
PatchOperation[]
```

要求：

- 至少包含一个 patch
- patch 顺序应与状态迁移顺序一致
- patch 必须能作用于当前 envelope

### rationale

类型：

```ts
string
```

要求：

- 1-3 句
- 解释为什么要这样迁移工作流
- 应与 patches 完全一致

### warnings

类型：

```ts
string[] | undefined
```

使用场景：

- 存在额外风险
- 存在策略冲突
- 需要人工确认

不要把普通解释写进 warnings。
