# 方案 2：后端优先 + user_tag 关联 — 实现计划

## Context

前端聊天消息仅存 localStorage，存在跨设备丢失、状态不一致、5MB 容量风险。后端已有 `ConversationMessage` 模型和查询，但：1) 模型没有 `user_tag` 字段，无法按用户隔离会话；2) 没有暴露给前端的加载消息 API。本方案让后端成为消息唯一真相源，localStorage 降级为只读缓存，并实现按 `user_tag` 隔离会话。

---

## 后端改动

### 1. Model 新增 `user_tag` 字段 — `app/models/agent_memory.py`

`ConversationMessage` 增加 `user_tag` 列：

```python
user_tag: Mapped[str] = mapped_column(String(100), nullable=False, default="default", index=True)
```

**注意：** 现有 SQLite 数据库不会自动新增此列（`create_all()` 不修改已有表）。需删除旧数据库文件后 `seed_data.py` 重建。

### 2. 更新 `BaseHistoryStore` 协议 — `app/agent/protocol.py`

`add_message` 和 `list_sessions` 增加 `user_tag` 参数：

```python
class BaseHistoryStore(Protocol):
    def get_messages(self, session_id: str) -> list[dict]: ...
    def add_message(self, session_id: str, message: dict, user_tag: str = "default") -> None: ...
    def clear(self, session_id: str) -> None: ...
    def list_sessions(self, user_tag: str | None = None) -> list[str]: ...
```

### 3. 更新 `InMemoryHistoryStore` — `app/agent/history.py`

- `add_message` 增加 `user_tag` 参数，存入内部结构（如 `_session_tags: dict[str, str]`）
- `list_sessions(user_tag)` 按存储的 tag 过滤

### 4. 更新 `SQLiteHistoryStore` — `app/agent/history.py`

- `add_message` 增加 `user_tag` 参数，写入 `data["user_tag"] = user_tag`
- `list_sessions(user_tag)` 调用 repo 的 `list_sessions_by_user_tag(user_tag)`

### 5. 新增 Repository 函数 — `app/repositories/agent_memory.py`

```python
def list_sessions_by_user_tag(user_tag: str) -> list[str]:
    with SessionLocal() as session:
        results = (
            session.query(MessageORM.session_id)
            .filter_by(user_tag=user_tag)
            .distinct()
            .order_by(MessageORM.session_id)
            .all()
        )
        return [r[0] for r in results]
```

### 6. 更新 `ReActAgent` — `app/agent/react_agent.py`

所有 `self._history.add_message(session_id, ...)` 调用增加 `user_tag=self._context.get("user_tag", "default")`。涉及位置：
- `chat()` 方法中的 user/assistant/tool 消息添加
- `chat_stream()` 方法中同样
- `_init_session()` 中的 system prompt 注入

### 7. 新增 Schema — `app/schemas/agent_memory.py`

```python
class ConversationMessageResponse(BaseModel):
    id: int
    role: str
    content: str | None = None
    tool_call_id: str | None = None
    tool_calls: str | None = None
    reasoning_content: str | None = None
    user_tag: str
    created_at: datetime

class ConversationMessageListResponse(BaseModel):
    messages: list[ConversationMessageResponse]
    total: int
```

### 8. 新增 Service 函数 — `app/services/agent_memory.py`

```python
def get_session_messages(session_id: str) -> ConversationMessageListResponse:
    messages = memory_repo.get_messages_by_session(session_id)
    return ConversationMessageListResponse(
        messages=[ConversationMessageResponse(**m) for m in messages],
        total=len(messages),
    )
```

### 9. 更新 Router — `app/agent/router.py`

**9a.** `GET /agent/sessions` 增加 `user_tag` 查询参数：

```python
@router.get("/sessions")
def get_sessions(user_tag: str | None = None):
    return {"sessions": _history_store.list_sessions(user_tag=user_tag)}
```

**9b.** 新增 `GET /agent/sessions/{session_id}/messages`：

```python
@router.get("/sessions/{session_id}/messages", response_model=ConversationMessageListResponse)
def get_session_messages(session_id: str):
    from app.services.agent_memory import get_session_messages as _get
    return _get(session_id)
```

---

## 前端改动

### 10. 新增类型 — `frontend/src/types/chat.ts`

```typescript
export interface BackendMessage {
  id: number
  role: string
  content: string | null
  tool_call_id?: string | null
  tool_calls?: string | null
  reasoning_content?: string | null
  user_tag: string
  created_at: string
}

export interface BackendMessageListResponse {
  messages: BackendMessage[]
  total: number
}
```

### 11. 更新 API — `frontend/src/api/chat.ts`

```typescript
export function getSessions(userTag: string) {
  return client.get<{ sessions: string[] }>('/agent/sessions', { params: { user_tag: userTag } })
}

export function getSessionMessages(sessionId: string) {
  return client.get<BackendMessageListResponse>(`/agent/sessions/${sessionId}/messages`)
}
```

`sendMessage` 和 `deleteSession` 中的 `ChatRequest` 已有 `user_tag` 字段，前端需传入。

### 12. 重构 Store — `frontend/src/stores/chat.ts`

**12a.** 新增 `userTag` ref（持久化到 localStorage）：

```typescript
const USER_TAG_KEY = 'hr-chat-user-tag'
const userTag = ref<string>(loadFromStorage(USER_TAG_KEY, 'default'))

watch(userTag, (val) => saveToStorage(USER_TAG_KEY, val))
```

**12b.** `fetchSessions` 传入 `userTag`，清理幽灵会话：

```typescript
async function fetchSessions() {
  try {
    const { data } = await chatApi.getSessions(userTag.value)
    const backendSessions = data.sessions
    for (const sid of backendSessions) {
      if (!sessions.value.includes(sid)) sessions.value.push(sid)
    }
    sessions.value = sessions.value.filter(sid =>
      backendSessions.includes(sid) || isStreamingForSession(sid)
    )
    if (!currentSessionId.value && sessions.value.length > 0) {
      currentSessionId.value = sessions.value[0]
    }
  } catch {
    if (!currentSessionId.value && sessions.value.length > 0) {
      currentSessionId.value = sessions.value[0]
    }
  }
}
```

**12c.** `selectSession` 始终从后端加载：

```typescript
async function selectSession(sessionId: string) {
  currentSessionId.value = sessionId
  isLoadingMessages.value = true
  try {
    const { data } = await chatApi.getSessionMessages(sessionId)
    messages.value[sessionId] = data.messages.map(toChatMessage)
  } catch {
    if (!messages.value[sessionId]) messages.value[sessionId] = []
  } finally {
    isLoadingMessages.value = false
  }
}
```

**12d.** `sendMessage` 传入 `userTag`（`ChatRequest` 已有此字段）。

**12e.** 新增 `setUserTag(tag)` 方法：切换 `userTag` 后清空当前 sessions/messages 并重新 `fetchSessions`。

**12f.** 导出 `userTag`, `isLoadingMessages`, `setUserTag`。

### 13. 更新 `useChat.ts` — `frontend/src/composables/useChat.ts`

```typescript
async function init() {
  await store.fetchSessions()
  if (store.currentSessionId) {
    await store.selectSession(store.currentSessionId)
  } else if (store.sessions.length === 0) {
    store.createSession()
  }
}
```

导出 `userTag`, `setUserTag`, `isLoadingMessages`。

### 14. user_tag 选择 UI — `frontend/src/components/SessionSidebar.vue`

在侧边栏顶部添加 `user_tag` 选择器（使用 `el-select` 或 `el-input`）：

```vue
<div class="user-tag-selector">
  <el-input v-model="userTag" placeholder="用户标识" @change="handleUserTagChange" />
</div>
```

切换 `userTag` 时调用 `store.setUserTag(newTag)` 清空并重新加载。

### 15. 加载状态 UI — `frontend/src/components/MessageList.vue`

```vue
<div v-if="isLoadingMessages" class="loading-messages">
  <el-icon class="is-loading"><Loading /></el-icon>
  <span>加载历史消息...</span>
</div>
```

---

## 关键文件清单

| 文件 | 操作 |
|---|---|
| `app/models/agent_memory.py` | `ConversationMessage` 增加 `user_tag` 列 |
| `app/agent/protocol.py` | `BaseHistoryStore` 协议增加 `user_tag` 参数 |
| `app/agent/history.py` | `InMemoryHistoryStore` + `SQLiteHistoryStore` 适配 `user_tag` |
| `app/repositories/agent_memory.py` | 新增 `list_sessions_by_user_tag` |
| `app/agent/react_agent.py` | 所有 `add_message` 调用传入 `user_tag` |
| `app/schemas/agent_memory.py` | 新增 `ConversationMessageResponse` + `ConversationMessageListResponse` |
| `app/services/agent_memory.py` | 新增 `get_session_messages` |
| `app/agent/router.py` | `GET /sessions` 加 `user_tag` 参数，新增 `GET /sessions/{id}/messages` |
| `frontend/src/types/chat.ts` | 新增 `BackendMessage` + `BackendMessageListResponse` |
| `frontend/src/api/chat.ts` | `getSessions` 加 `userTag` 参数，新增 `getSessionMessages` |
| `frontend/src/stores/chat.ts` | 重构：`userTag` 状态、`selectSession` 后端加载、`fetchSessions` 按 tag 过滤、`setUserTag` |
| `frontend/src/composables/useChat.ts` | 改造 `init`，导出 `userTag`/`setUserTag`/`isLoadingMessages` |
| `frontend/src/components/SessionSidebar.vue` | 添加 `user_tag` 选择器 |
| `frontend/src/components/MessageList.vue` | 添加加载中 UI |

## 验证

1. 删除旧数据库，运行 `seed_data.py` 重建
2. 启动后端，确认 `GET /agent/sessions?user_tag=default` 返回正确过滤结果
3. 确认 `GET /agent/sessions/{session_id}/messages` 返回消息列表
4. 启动前端，输入不同 `user_tag`，确认会话列表隔离
5. 切换 `user_tag`，确认会话列表清空并重新加载
6. 发送消息后刷新页面，确认消息从后端恢复
7. 清除 localStorage，刷新页面，确认消息仍从后端加载
8. 停掉后端，切换 session，确认 fallback 到本地缓存不报错
