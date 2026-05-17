# Codex Models 重构规范

## 1. 文档目的

本文档用于沉淀本仓库在 `models` 层重构时对 Codex 的固定要求，作为后续同类改造的统一执行规范。

目标是让 Codex 在处理 `models` 重构任务时，始终遵守相同的边界、实现风格、兼容性要求和文档同步要求，避免再次出现业务模型、agent 运行时模型和数据库约束策略混杂的问题。

本文档既是仓库内部规范，也是给 Codex 的长期任务指令来源。

## 2. 适用范围

本文档适用于以下改动：

- `app/models` 下的业务领域模型重构
- `app/agent/models` 下的 agent 运行时模型重构
- 与模型重构相关的 `repository / schema / service` 对齐调整
- 与模型边界相关的 `README.md` 和 `docs/` 文档同步

如果任务涉及数据模型边界、模型拆分、命名重构、外键策略或模型注释补充，默认适用本规范。

## 3. 强制规则

### 3.1 业务模型与 agent 模型分边界

- `app/models` 只放业务领域模型
- `app/agent/models` 只放 agent 运行时模型
- agent 相关模型不得重新混入业务 `models` 聚合边界

这意味着：

- `AgentMemory`
- `MemoryReminder`
- `ConversationMessage`

这类模型应归属 `app/agent/models`，而不是 `app/models`。

### 3.2 models 层禁止使用数据库外键

`models` 层禁止使用：

```python
ForeignKey(...)
```

所有关联字段都应使用普通标量列，例如 `Integer`、`String`。

如果需要表达 ORM 关系，必须在 ORM 层显式写出连接条件，而不是依赖数据库外键推导。

### 3.3 base.py 不保留 fk 命名暗示

`app/models/base.py` 中的 `Base.metadata.naming_convention` 不应保留 `"fk"` 命名规则。

如果仓库决定采用无数据库外键方案，那么基础命名约定也应与这一策略一致，避免继续向实现者暗示会存在 FK 约束。

### 3.4 ORM 关系必须显式表达

如果模型之间仍然需要关系导航，应使用：

- `relationship(...)`
- `primaryjoin=...`
- `foreign_keys=...`
- 必要时使用 `remote(...)`

典型形式如下：

```python
relationship(
    "TargetModel",
    primaryjoin="foreign(SourceModel.target_id) == TargetModel.id",
    foreign_keys=[target_id],
)
```

不得依赖 `ForeignKey(...)` 自动推导关系。

### 3.5 `app/models/__init__.py` 只导出业务模型

- `app/models/__init__.py` 只导出业务模型
- agent 运行时模型不加入 `app.models.__all__`
- agent 模型应通过 `app/agent/models/__init__.py` 自己导出

如果为了兼容旧代码短期保留：

```text
app/models/agent_memory.py
```

这种文件必须明确标注为过渡兼容层，而不是正式归属。

### 3.6 models 层需要中文注释

`models` 层应补充中文注释，至少覆盖：

- 模块职责
- 模型类职责
- 少数关键关系块或关键字段组

不要求对每个字段逐行解释，但不允许整个模型层长期处于“只有英文代码、没有中文上下文”的状态。

### 3.7 README 和 docs 必须同步

只要 `models` 层边界发生变化，就必须同步检查并更新：

- `README.md`
- `docs/` 下与模型结构、架构边界相关的文档

至少要保证：

- `app/models` 的描述与“业务模型 only”一致
- `app/agent/models` 的存在和职责在文档中得到体现

### 3.8 兼容旧调用方

如果旧的：

- `repository`
- `schema`
- `service`
- `router`

依赖了现有模型字段名或导入路径，重构时必须满足其一：

1. 保持兼容
2. 明确提供迁移方案
3. 明确提供临时过渡层

不能只改模型，不处理调用方影响。

## 4. 推荐实现方式

### 4.1 目录组织

推荐使用以下边界：

```text
app/
  models/          # 业务领域模型
  agent/
    models/        # agent 运行时模型
```

### 4.2 统一基础设施

优先复用 `app/models/base.py` 中的基础设施：

- `Base`
- `IdentityMixin`
- `TimestampMixin`
- `DictMixin`

这样业务模型和 agent 模型可以共享统一的主键、时间戳和序列化风格。

### 4.3 无外键但保留关系表达

如果需要同时满足“无数据库外键”和“保留 ORM 关系”，优先采用以下方式：

1. 关联字段定义为普通 `Integer` / `String`
2. `relationship` 显式写 `primaryjoin`
3. 明确写出 `foreign_keys`
4. 自关联场景下按需使用 `remote`

### 4.4 先保字段兼容，再做命名清理

当 `repository / schema / service` 已经依赖字段名时：

- 优先保证字段名兼容
- 再考虑后续渐进式清理旧导入路径或旧文件位置

不要在同一轮里同时打断字段契约、导入路径和边界结构，除非该任务明确要求全量联动重构。

### 4.5 中文注释的推荐粒度

推荐注释粒度如下：

- 文件开头：一句中文模块说明
- 每个模型类：一句中文职责说明
- 关键关系块：必要时补一条中文说明

不建议把注释写成逐字段手册，也不建议完全不写。

## 5. 重构验收清单

完成 `models` 重构后，Codex 必须自检以下事项：

### 5.1 边界检查

- `app/models` 是否只包含业务领域模型
- `app/agent/models` 是否承载 agent 运行时模型
- agent 模型是否没有重新混入 `app/models/__init__.py`

### 5.2 外键策略检查

下面的搜索结果应为空：

```bash
rg -n "ForeignKey" app/models app/agent/models
```

### 5.3 base.py 检查

- `app/models/base.py` 中不应存在 `"fk"` naming convention

### 5.4 关系表达检查

- 仍需导航的模型关系是否使用显式 `relationship + primaryjoin + foreign_keys`
- 自关联关系是否正确使用 `remote`

### 5.5 注释检查

- 模块级中文注释是否存在
- 主要模型类是否有中文职责说明

### 5.6 文档同步检查

- `README.md` 是否已同步新的模型边界
- 相关 `docs/` 文档是否已同步新的模型边界

### 5.7 兼容性检查

- 旧 `repository / schema / service` 依赖的字段名是否仍可工作
- 如不能兼容，是否已提供明确迁移方案或兼容层

### 5.8 静态检查

至少应对变更范围运行一次静态检查，例如：

```bash
ruff check app/models app/agent/models --no-cache
```

如果只改了单个兼容层文件，也要把该文件纳入检查范围。

## 6. 可复用 Codex Prompt 模板

下面这段文字可以直接复制给 Codex，作为 `models` 重构任务提示词。

```text
请重构本仓库的 models 层，并严格遵守以下规则：

1. app/models 只保留业务领域模型，不要把 agent 运行时模型放进去。
2. agent 相关模型必须放到 app/agent/models。
3. models 层禁止使用 ForeignKey(...)。
4. app/models/base.py 中不要保留 fk naming convention。
5. 如果需要表达关系，请使用 relationship + primaryjoin + foreign_keys，必要时使用 remote。
6. app/models/__init__.py 只导出业务模型；agent models 不要混入 app.models.__all__。
7. models 层需要补中文注释，至少包括模块职责、模型类职责和关键关系说明。
8. 如果旧 repository/schema/service 依赖字段名或导入路径，请保持兼容，或明确提供迁移方案/兼容层。
9. 只要模型边界发生变化，请同步更新 README 和相关 docs。
10. 完成后自检：
   - rg -n "ForeignKey" app/models app/agent/models 结果为空
   - base.py 没有 fk naming convention
   - README 已同步
   - agent 模型和业务模型边界清晰
   - 变更范围通过 ruff check

如果任务中包含 agent memory、conversation、reminder 一类模型，请默认把它们视为 agent 运行时模型，而不是业务领域模型。
```

## 7. 默认执行结论

如果用户只说“重构 models 层”而没有补充更多约束，Codex 应默认采用以下结论：

- 业务模型留在 `app/models`
- agent 运行时模型放到 `app/agent/models`
- 不使用数据库外键
- 使用显式 ORM join 表达关系
- 删除 `base.py` 中的 `fk` 命名规则
- 保持字段契约兼容
- 补中文注释
- 同步 README 和 docs

以上默认值除非用户明确推翻，否则视为本仓库中的标准做法。
