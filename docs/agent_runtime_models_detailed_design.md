# Agent 运行时 Models 详细设计

## 1. 文档目的

本文档用于沉淀此前从 `app/models` 中拆出的 agent 相关模型设计，作为后续在独立边界中重新实现的依据。

目标是明确以下内容：

- agent 运行时模型应放在哪里
- 需要实现哪些实体
- 每个实体的字段、类型、索引、约束和职责
- 模型之间如何关联
- 在“不使用数据库外键”的前提下如何表达关系
- 当前 `repository / service / schema / router` 层已经隐含依赖了哪些字段与行为

本文档面向“按设计实现”的开发方式，因此默认实现者会根据本文直接编写模型，而不是再从旧代码逆向猜测。

## 2. 边界与目录

### 2.1 设计边界

这批模型属于 **agent 运行时数据**，不是制造现场业务真相。

因此它们不应继续放在：

```text
app/models
```

而应放在独立命名空间：

```text
app/agent/models
```

### 2.2 推荐目录结构

```text
app/
  agent/
    models/
      __init__.py
      memory.py
      conversation.py
```

### 2.3 与业务模型的关系

- `app/models` 只保留业务领域模型
- `app/agent/models` 只保留 agent 运行时模型
- 两边都可以复用同一个 SQLAlchemy `Base`
- 两边都不通过 `app/models/__init__.py` 混合导出

如果需要兼容旧代码导入路径，可以临时提供一个过渡层：

```text
app/models/agent_memory.py
```

但这只是兼容层，不是正式归属。

## 3. 设计原则

### 3.1 不使用数据库外键

本项目 models 层采用“无数据库外键”方案，因此 agent models 也应保持一致：

- 关联字段使用普通 `Integer` / `String`
- 不使用 `ForeignKey(...)`
- 如需 ORM 关系，使用 `relationship(..., primaryjoin=..., foreign_keys=...)`

例如：

```python
memory_id: Mapped[int] = mapped_column(Integer, nullable=False)

memory: Mapped["AgentMemory"] = relationship(
    "AgentMemory",
    back_populates="reminders",
    primaryjoin="foreign(MemoryReminder.memory_id) == AgentMemory.id",
    foreign_keys=[memory_id],
)
```

### 3.2 复用统一基础设施

推荐复用 `app/models/base.py` 中的公共 mixin：

- `Base`
- `IdentityMixin`
- `TimestampMixin`
- `DictMixin`

其中：

- `AgentMemory`、`ConversationMessage` 需要 `created_at / updated_at`
- `MemoryReminder` 只要求 `created_at`，不强制 `updated_at`

### 3.3 `to_dict()` 输出规则

`to_dict()` 只输出列字段，不展开 relationship。

原因：

- repository 当前直接返回 `model.to_dict()`
- schema 当前按扁平字段结构接收数据
- 避免消息、提醒、记忆之间递归展开

### 3.4 中文注释要求

和业务 models 一样，建议为 agent models 添加中文注释：

- 文件级模块说明
- 类职责说明
- 少量关键关系注释

不需要为每个字段逐行写说明性废话。

## 4. 实体总览

需要恢复的实体共 3 个：

1. `AgentMemory`
2. `MemoryReminder`
3. `ConversationMessage`

对应职责如下：

| 实体 | 职责 |
| --- | --- |
| `AgentMemory` | 保存 agent 的长期记忆条目 |
| `MemoryReminder` | 保存挂在记忆条目上的提醒任务 |
| `ConversationMessage` | 保存会话中的消息、工具调用痕迹和推理文本 |

## 5. AgentMemory 设计

### 5.1 职责

`AgentMemory` 表示 agent 在会话运行过程中沉淀下来的长期记忆条目。

它主要用于保存：

- 事实类记忆
- 偏好类记忆
- 观察类记忆
- 上下文类记忆
- 可演化为提醒的记忆

### 5.2 表名

推荐表名：

```text
agent_memories
```

### 5.3 字段设计

| 字段 | 类型 | 必填 | 说明 |
| --- | --- | --- | --- |
| `id` | `int` | 是 | 主键 |
| `session_id` | `str` | 是 | 来源会话 ID |
| `user_tag` | `str \| None` | 否 | 用户标识，用于按用户召回记忆 |
| `memory_type` | `str` | 是 | 记忆类型 |
| `category` | `str` | 是 | 业务分类 |
| `subject` | `str` | 是 | 记忆主题 |
| `content` | `str` | 是 | 记忆正文 |
| `source` | `str` | 是 | 记忆来源 |
| `importance` | `int` | 是 | 重要等级，默认 3 |
| `expires_at` | `datetime \| None` | 否 | 过期时间 |
| `is_active` | `bool` | 是 | 是否激活，默认 `True` |
| `created_at` | `datetime` | 是 | 创建时间 |
| `updated_at` | `datetime` | 是 | 更新时间 |

### 5.4 枚举/取值范围

根据 `app/schemas/agent_memory.py`，当前有效值如下：

#### `memory_type`

```python
{"fact", "observation", "preference", "reminder", "context"}
```

#### `category`

```python
{"onboarding", "project", "employee", "analytics", "general"}
```

#### `source`

```python
{"agent_observed", "user_instructed", "system_detected"}
```

模型层不强制写数据库 check constraint，但字段命名和类型必须支持这些值。

### 5.5 索引设计

建议索引：

1. `("user_tag", "created_at")`
2. `("subject")`
3. `("is_active", "expires_at")`

原因：

- repository 存在按 `user_tag` 召回和按时间倒序读取
- repository 存在按 `subject` 查询
- 清理过期记忆时需要按 `is_active + expires_at` 过滤

### 5.6 relationship 设计

`AgentMemory` 需要和 `MemoryReminder` 建立一对多关系：

- 一个记忆可以挂多个提醒
- 删除记忆时，提醒应一起删除

推荐：

```python
reminders: Mapped[list["MemoryReminder"]] = relationship(
    "MemoryReminder",
    back_populates="memory",
    cascade="all, delete-orphan",
)
```

### 5.7 repository 隐含行为要求

从 `app/repositories/agent_memory.py` 可以反推出 `AgentMemory` 需要支持以下查询/更新：

1. `session.get(AgentMemory, memory_id)`
2. `filter_by(user_tag=...)`
3. `filter_by(memory_type=...)`
4. `filter_by(category=...)`
5. `filter_by(subject=...)`
6. `filter(AgentMemory.content.ilike(...))`
7. `filter(AgentMemory.importance >= min_importance)`
8. `filter(AgentMemory.expires_at.isnot(None))`
9. `filter(AgentMemory.expires_at <= datetime.now())`
10. `update({AgentMemory.is_active: False})`

因此字段名必须与当前 repository 预期完全一致。

### 5.8 业务特例

当前 service 层对 `preference` 型记忆有一个特殊语义：

- 当 `memory_type == "preference"` 且存在同一 `user_tag + subject` 的激活记录时
- 不新增新记录
- 而是更新现有记录的 `content / importance / updated_at`

因此实现时不需要在数据库层做唯一约束，但应确保这些字段存在且可被高频更新。

## 6. MemoryReminder 设计

### 6.1 职责

`MemoryReminder` 表示挂在长期记忆上的提醒任务。

它的作用不是独立记忆，而是：

- 指定何时触发
- 指定是否为循环提醒
- 记录是否已触发
- 记录触发次数

### 6.2 表名

推荐表名：

```text
memory_reminders
```

### 6.3 字段设计

| 字段 | 类型 | 必填 | 说明 |
| --- | --- | --- | --- |
| `id` | `int` | 是 | 主键 |
| `memory_id` | `int` | 是 | 所属记忆 ID |
| `reminder_type` | `str` | 是 | 提醒类型 |
| `trigger_at` | `datetime` | 是 | 触发时间 |
| `recurrence_rule` | `str \| None` | 否 | 循环规则字符串 |
| `triggered` | `bool` | 是 | 是否已触发，默认 `False` |
| `trigger_count` | `int` | 是 | 触发次数，默认 `0` |
| `created_at` | `datetime` | 是 | 创建时间 |

### 6.4 枚举/取值范围

根据 `app/schemas/agent_memory.py`：

```python
{"one_time", "recurring"}
```

### 6.5 索引设计

建议索引：

1. `("memory_id")`
2. `("trigger_at", "triggered")`

原因：

- repository 有 `get_reminders_by_memory(memory_id)`
- repository 有按 `trigger_at <= before and not triggered` 的待触发查询

### 6.6 relationship 设计

`MemoryReminder` 需要回连到 `AgentMemory`：

```python
memory: Mapped["AgentMemory"] = relationship(
    "AgentMemory",
    back_populates="reminders",
    primaryjoin="foreign(MemoryReminder.memory_id) == AgentMemory.id",
    foreign_keys=[memory_id],
)
```

### 6.7 repository 隐含行为要求

当前 repository 需要支持：

1. `session.get(ReminderORM, reminder_id)`
2. `filter_by(memory_id=memory_id)`
3. `join(MemoryORM, ReminderORM.memory_id == MemoryORM.id)`
4. `filter(ReminderORM.trigger_at <= before)`
5. `filter(~ReminderORM.triggered)`
6. `r.triggered = True`
7. `r.trigger_count += 1`

因此：

- `triggered` 必须是布尔字段
- `trigger_count` 必须是整数
- `memory_id` 必须是可用于 join 的普通整数字段

## 7. ConversationMessage 设计

### 7.1 职责

`ConversationMessage` 表示 agent 会话中的消息历史。

除了普通 `user / assistant` 消息，它还要承载：

- tool call id
- 工具调用序列化内容
- reasoning 文本

因此它不仅是“聊天记录”，也是 agent 推理与工具调用的轻量轨迹表。

### 7.2 表名

推荐表名：

```text
conversation_messages
```

### 7.3 字段设计

| 字段 | 类型 | 必填 | 说明 |
| --- | --- | --- | --- |
| `id` | `int` | 是 | 主键 |
| `session_id` | `str` | 是 | 会话 ID |
| `user_tag` | `str` | 是 | 用户标识 |
| `role` | `str` | 是 | 消息角色 |
| `content` | `str \| None` | 否 | 消息正文 |
| `tool_call_id` | `str \| None` | 否 | 工具调用 ID |
| `tool_calls` | `str \| None` | 否 | 工具调用序列化结果 |
| `reasoning_content` | `str \| None` | 否 | 推理内容 |
| `created_at` | `datetime` | 是 | 创建时间 |
| `updated_at` | `datetime` | 是 | 更新时间 |

### 7.4 索引设计

建议索引：

1. `("session_id", "created_at")`
2. `("user_tag", "session_id")`

原因：

- repository 存在按 `session_id` 正序拉取消息
- repository 存在按 `session_id` 统计与删除
- repository 存在按 `user_tag` 列出 sessions

### 7.5 repository 隐含行为要求

当前 repository 需要支持：

1. `filter_by(session_id=session_id).order_by(created_at.asc())`
2. `filter_by(session_id=session_id).count()`
3. `filter_by(session_id=session_id).delete()`
4. `query(MessageORM.session_id).distinct()`
5. `filter_by(user_tag=user_tag).distinct()`
6. `order_by(created_at.desc()).limit(max_messages)`
7. `id.notin_(keep_id_set)` 用于裁剪消息历史

因此：

- `session_id` 必须是稳定字符串字段
- `created_at` 必须可排序
- `user_tag` 必须存在，且不应为缺失字段

### 7.6 role 字段说明

当前 schema 没有限定 `role` 枚举，但实践上应允许至少以下值：

- `user`
- `assistant`
- `system`
- `tool`

模型层可以不做数据库约束，但文档上应明确这个语义范围。

## 8. 三个实体之间的关系

```text
AgentMemory 1 -> N MemoryReminder

ConversationMessage
  - 独立存在
  - 不直接依赖 AgentMemory
  - 通过 session_id / user_tag 与会话上下文关联
```

关键点：

- `MemoryReminder` 是 `AgentMemory` 的子对象
- `ConversationMessage` 不应强行绑定到某条记忆
- 记忆和消息都可以通过 `session_id`、`user_tag` 在服务层建立语义联系

## 9. 对外导出设计

### 9.1 `app/agent/models/__init__.py`

应统一导出：

- `AgentMemory`
- `MemoryReminder`
- `ConversationMessage`

### 9.2 不导入业务 models 聚合

不要把上述实体重新加入：

```python
app.models.__all__
```

原因：

- 这会重新污染业务模型边界
- 违反“业务模型 / agent 运行时模型分离”的目标

### 9.3 兼容导入策略

如果当前仍有老代码依赖：

```python
from app.models.agent_memory import ...
```

可以短期保留一个兼容文件：

```python
app/models/agent_memory.py
```

内容只做转发：

```python
from app.agent.models import AgentMemory, ConversationMessage, MemoryReminder
```

后续待 repository / service 完成切换后再删除。

## 10. 与现有 schema 的对齐要求

实现必须与 `app/schemas/agent_memory.py` 对齐。

### 10.1 MemoryResponse 对齐字段

模型必须能输出：

- `id`
- `session_id`
- `user_tag`
- `memory_type`
- `category`
- `subject`
- `content`
- `source`
- `importance`
- `expires_at`
- `is_active`
- `created_at`
- `updated_at`

### 10.2 ReminderResponse 对齐字段

模型必须能输出：

- `id`
- `memory_id`
- `reminder_type`
- `trigger_at`
- `recurrence_rule`
- `triggered`
- `trigger_count`
- `created_at`

### 10.3 ConversationMessageResponse 对齐字段

模型必须能输出：

- `id`
- `role`
- `content`
- `tool_call_id`
- `tool_calls`
- `reasoning_content`
- `user_tag`
- `created_at`

注意：response schema 当前不要求 `updated_at`，但模型层保留它没有问题。

## 11. 与现有 repository 的对齐要求

实现必须兼容 `app/repositories/agent_memory.py` 当前的访问方式。

重点是下面这些名字不能改：

- `AgentMemory.user_tag`
- `AgentMemory.memory_type`
- `AgentMemory.category`
- `AgentMemory.subject`
- `AgentMemory.content`
- `AgentMemory.importance`
- `AgentMemory.expires_at`
- `AgentMemory.is_active`
- `MemoryReminder.memory_id`
- `MemoryReminder.trigger_at`
- `MemoryReminder.triggered`
- `MemoryReminder.trigger_count`
- `ConversationMessage.session_id`
- `ConversationMessage.user_tag`
- `ConversationMessage.created_at`

如果这些名字改动，repository 会立刻失效。

## 12. 推荐实现草图

### 12.1 `memory.py`

应包含：

- `AgentMemory`
- `MemoryReminder`

并复用：

- `Base`
- `IdentityMixin`
- `TimestampMixin`
- `DictMixin`

### 12.2 `conversation.py`

应包含：

- `ConversationMessage`

### 12.3 示例实现骨架

```python
class AgentMemory(Base, IdentityMixin, TimestampMixin, DictMixin):
    __tablename__ = "agent_memories"

    session_id: Mapped[str] = mapped_column(String(80), nullable=False)
    user_tag: Mapped[str | None] = mapped_column(String(80), nullable=True)
    memory_type: Mapped[str] = mapped_column(String(30), nullable=False)
    category: Mapped[str] = mapped_column(String(40), nullable=False)
    subject: Mapped[str] = mapped_column(String(120), nullable=False)
    content: Mapped[str] = mapped_column(Text, nullable=False)
    source: Mapped[str] = mapped_column(String(40), nullable=False)
    importance: Mapped[int] = mapped_column(Integer, nullable=False, default=3)
    expires_at: Mapped[datetime | None] = mapped_column(DateTime, nullable=True)
    is_active: Mapped[bool] = mapped_column(Boolean, nullable=False, default=True)
```

## 13. 验收标准

实现完成后，至少满足以下验收条件：

1. `app.agent.models` 可以独立导入
2. `app.models.__all__` 不包含 agent models
3. 全部 agent models 不使用 `ForeignKey(...)`
4. repository 中现有查询、更新、删除逻辑可直接工作
5. `to_dict()` 输出字段与 schema 对齐
6. `ConversationMessage` 可按 `session_id` 正序读取
7. `AgentMemory` 可按 `user_tag` / `subject` / `content` / `importance` 查询
8. `MemoryReminder` 可按 `trigger_at` / `triggered` 检索待触发项

## 14. 默认选择

如果实现时没有额外产品要求，默认采用以下选择：

- 使用 `app/agent/models` 作为正式目录
- 使用无数据库外键方案
- 保留与旧 repository/schema 完全一致的字段命名
- `AgentMemory`、`ConversationMessage` 继承 `TimestampMixin`
- `MemoryReminder` 只保留 `created_at`
- `ConversationMessage` 不直接关联 `AgentMemory`
- 短期允许 `app/models/agent_memory.py` 作为兼容转发层

