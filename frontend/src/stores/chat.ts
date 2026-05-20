import { defineStore } from 'pinia'
import { ref, watch } from 'vue'
import type { BackendMessage, ChatMessage, OnboardingCaseSummary, ToolCallInfo } from '../types/chat'
import * as chatApi from '../api/chat'
import { streamChat } from '../api/sse'

const STORAGE_KEY = 'hr-chat-messages'
const SESSIONS_KEY = 'hr-chat-sessions'
const USER_TAG_KEY = 'hr-chat-user-tag'

function generateId(): string {
  return crypto.randomUUID()
}

function loadFromStorage<T>(key: string, fallback: T): T {
  try {
    const raw = localStorage.getItem(key)
    return raw ? JSON.parse(raw) : fallback
  } catch {
    return fallback
  }
}

function saveToStorage(key: string, value: unknown) {
  localStorage.setItem(key, JSON.stringify(value))
}

function parseToolCalls(raw?: string | null): ToolCallInfo[] | undefined {
  if (!raw) return undefined
  try {
    const parsed = JSON.parse(raw)
    if (!Array.isArray(parsed)) return undefined
    const names = parsed
      .map((tc) => tc?.function?.name)
      .filter((name): name is string => typeof name === 'string' && name.length > 0)
    return names.length > 0 ? [{ names, status: 'completed' }] : undefined
  } catch {
    return undefined
  }
}

function toChatMessage(message: BackendMessage): ChatMessage | null {
  if (message.role !== 'user' && message.role !== 'assistant') return null
  return {
    id: String(message.id),
    role: message.role,
    content: message.content || '',
    timestamp: new Date(message.created_at).getTime(),
    toolCalls: parseToolCalls(message.tool_calls),
  }
}

export const useChatStore = defineStore('chat', () => {
  const sessions = ref<string[]>(loadFromStorage(SESSIONS_KEY, []))
  const currentSessionId = ref<string | null>(null)
  const messages = ref<Record<string, ChatMessage[]>>(loadFromStorage(STORAGE_KEY, {}))
  const userTag = ref<string>(loadFromStorage(USER_TAG_KEY, 'default'))
  const onboardingCases = ref<Record<string, OnboardingCaseSummary | null>>({})
  const isLoadingMessages = ref(false)
  const isStreaming = ref(false)
  const streamingMessageId = ref<string | null>(null)
  const abortController = ref<AbortController | null>(null)

  watch([sessions, messages], () => {
    saveToStorage(SESSIONS_KEY, sessions.value)
    saveToStorage(STORAGE_KEY, messages.value)
  }, { deep: true })

  watch(userTag, () => {
    saveToStorage(USER_TAG_KEY, userTag.value)
  })

  function isStreamingForSession(sessionId: string): boolean {
    return isStreaming.value && currentSessionId.value === sessionId
  }

  async function fetchSessions() {
    try {
      const { data } = await chatApi.getSessions(userTag.value)
      const backendSessions = data.sessions
      for (const sid of backendSessions) {
        if (!sessions.value.includes(sid)) {
          sessions.value.push(sid)
        }
      }
      sessions.value = sessions.value.filter(sid =>
        backendSessions.includes(sid) || isStreamingForSession(sid),
      )
      if (!currentSessionId.value && sessions.value.length > 0) {
        currentSessionId.value = sessions.value[0]
      }
    } catch {
      // Backend may be unreachable; use local sessions
      if (!currentSessionId.value && sessions.value.length > 0) {
        currentSessionId.value = sessions.value[0]
      }
    }
  }

  async function selectSession(sessionId: string) {
    currentSessionId.value = sessionId
    isLoadingMessages.value = true
    try {
      const { data } = await chatApi.getSessionMessages(sessionId)
      messages.value[sessionId] = data.messages
        .map(toChatMessage)
        .filter((msg): msg is ChatMessage => msg !== null)
    } catch {
      if (!messages.value[sessionId]) messages.value[sessionId] = []
    } finally {
      isLoadingMessages.value = false
    }
    await fetchSessionState(sessionId)
  }

  function createSession(): string {
    const id = generateId()
    sessions.value.unshift(id)
    messages.value[id] = []
    onboardingCases.value[id] = null
    currentSessionId.value = id
    return id
  }

  async function deleteSession(sessionId: string) {
    try {
      await chatApi.deleteSession(sessionId, userTag.value)
    } catch { /* ignore */ }
    sessions.value = sessions.value.filter(s => s !== sessionId)
    delete messages.value[sessionId]
    delete onboardingCases.value[sessionId]
    if (currentSessionId.value === sessionId) {
      currentSessionId.value = sessions.value[0] || null
    }
  }

  async function fetchSessionState(sessionId: string) {
    try {
      const { data } = await chatApi.getSessionState(sessionId, userTag.value)
      onboardingCases.value[sessionId] = data.onboarding_case || null
    } catch {
      onboardingCases.value[sessionId] = null
    }
  }

  function currentMessages(): ChatMessage[] {
    if (!currentSessionId.value) return []
    return messages.value[currentSessionId.value] || []
  }

  async function sendMessage(text: string) {
    if (!text.trim() || isStreaming.value) return

    let sessionId = currentSessionId.value
    if (!sessionId) {
      sessionId = createSession()
    }

    const userMsg: ChatMessage = {
      id: generateId(),
      role: 'user',
      content: text.trim(),
      timestamp: Date.now(),
    }
    if (!messages.value[sessionId]) messages.value[sessionId] = []
    messages.value[sessionId].push(userMsg)

    const assistantMsg: ChatMessage = {
      id: generateId(),
      role: 'assistant',
      content: '',
      timestamp: Date.now(),
      toolCalls: [],
      isStreaming: true,
    }
    messages.value[sessionId].push(assistantMsg)

    isStreaming.value = true
    streamingMessageId.value = assistantMsg.id
    const ctrl = new AbortController()
    abortController.value = ctrl

    try {
      await streamChat(
        { message: text.trim(), session_id: sessionId, user_tag: userTag.value },
        {
          onMessage(delta) {
            const msg = messages.value[sessionId!]?.find(m => m.id === assistantMsg.id)
            if (msg) msg.content += delta
          },
          onToolCall(names) {
            const msg = messages.value[sessionId!]?.find(m => m.id === assistantMsg.id)
            if (msg) {
              msg.toolCalls = msg.toolCalls || []
              msg.toolCalls = msg.toolCalls.filter(tc => tc.status !== 'calling')
              msg.toolCalls.push({ names, status: 'calling' })
            }
          },
          onToolResult(names) {
            const msg = messages.value[sessionId!]?.find(m => m.id === assistantMsg.id)
            if (msg) {
              msg.toolCalls = msg.toolCalls || []
              const calling = msg.toolCalls.find(tc => tc.status === 'calling')
              if (calling) calling.status = 'completed'
              else msg.toolCalls.push({ names, status: 'completed' })
            }
            void fetchSessionState(sessionId!)
          },
          onDone(serverSessionId) {
            if (serverSessionId && sessionId !== serverSessionId) {
              messages.value[serverSessionId] = messages.value[sessionId!]
              onboardingCases.value[serverSessionId] = onboardingCases.value[sessionId!] || null
              delete messages.value[sessionId!]
              delete onboardingCases.value[sessionId!]
              const idx = sessions.value.indexOf(sessionId!)
              if (idx !== -1) sessions.value[idx] = serverSessionId
              currentSessionId.value = serverSessionId
              sessionId = serverSessionId
            }
            void fetchSessionState(sessionId!)
            finalizeStream()
          },
          onError(error) {
            const msg = messages.value[sessionId!]?.find(m => m.id === assistantMsg.id)
            if (msg) {
              msg.isError = true
              msg.content += `\n\n**错误**: ${error}`
            }
            finalizeStream()
          },
        },
        ctrl,
      )
    } catch (err) {
      if (!ctrl.signal.aborted) {
        const msg = messages.value[sessionId]?.find(m => m.id === assistantMsg.id)
        if (msg) {
          msg.isError = true
          msg.content += '\n\n**错误**: 网络连接失败'
        }
      }
      finalizeStream()
    }
  }

  function finalizeStream() {
    const sid = currentSessionId.value
    if (sid && streamingMessageId.value) {
      const msg = messages.value[sid]?.find(m => m.id === streamingMessageId.value)
      if (msg) msg.isStreaming = false
    }
    isStreaming.value = false
    streamingMessageId.value = null
    abortController.value = null
  }

  function stopStreaming() {
    if (abortController.value) {
      abortController.value.abort()
    }
    finalizeStream()
  }

  async function setUserTag(tag: string) {
    const normalized = tag.trim() || 'default'
    if (normalized === userTag.value) return
    userTag.value = normalized
    sessions.value = []
    messages.value = {}
    onboardingCases.value = {}
    currentSessionId.value = null
    await fetchSessions()
    if (currentSessionId.value) {
      await selectSession(currentSessionId.value)
    } else {
      createSession()
    }
  }

  return {
    sessions,
    currentSessionId,
    messages,
    onboardingCases,
    userTag,
    isLoadingMessages,
    isStreaming,
    streamingMessageId,
    fetchSessions,
    selectSession,
    createSession,
    deleteSession,
    fetchSessionState,
    currentMessages,
    sendMessage,
    stopStreaming,
    setUserTag,
  }
})
