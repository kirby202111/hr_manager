import { defineStore } from 'pinia'
import { ref, watch } from 'vue'
import type { ChatMessage } from '../types/chat'
import * as chatApi from '../api/chat'
import { streamChat } from '../api/sse'

const STORAGE_KEY = 'hr-chat-messages'
const SESSIONS_KEY = 'hr-chat-sessions'

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

export const useChatStore = defineStore('chat', () => {
  const sessions = ref<string[]>(loadFromStorage(SESSIONS_KEY, []))
  const currentSessionId = ref<string | null>(null)
  const messages = ref<Record<string, ChatMessage[]>>(loadFromStorage(STORAGE_KEY, {}))
  const isStreaming = ref(false)
  const streamingMessageId = ref<string | null>(null)
  const abortController = ref<AbortController | null>(null)

  watch([sessions, messages], () => {
    saveToStorage(SESSIONS_KEY, sessions.value)
    saveToStorage(STORAGE_KEY, messages.value)
  }, { deep: true })

  async function fetchSessions() {
    try {
      const { data } = await chatApi.getSessions()
      const backendSessions = data.sessions
      for (const sid of backendSessions) {
        if (!sessions.value.includes(sid)) {
          sessions.value.push(sid)
        }
      }
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

  function selectSession(sessionId: string) {
    currentSessionId.value = sessionId
  }

  function createSession(): string {
    const id = generateId()
    sessions.value.unshift(id)
    messages.value[id] = []
    currentSessionId.value = id
    return id
  }

  async function deleteSession(sessionId: string) {
    try {
      await chatApi.deleteSession(sessionId)
    } catch { /* ignore */ }
    sessions.value = sessions.value.filter(s => s !== sessionId)
    delete messages.value[sessionId]
    if (currentSessionId.value === sessionId) {
      currentSessionId.value = sessions.value[0] || null
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
        { message: text.trim(), session_id: sessionId },
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
          },
          onDone(serverSessionId) {
            if (serverSessionId && sessionId !== serverSessionId) {
              messages.value[serverSessionId] = messages.value[sessionId!]
              delete messages.value[sessionId!]
              const idx = sessions.value.indexOf(sessionId!)
              if (idx !== -1) sessions.value[idx] = serverSessionId
              currentSessionId.value = serverSessionId
              sessionId = serverSessionId
            }
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

  return {
    sessions,
    currentSessionId,
    messages,
    isStreaming,
    streamingMessageId,
    fetchSessions,
    selectSession,
    createSession,
    deleteSession,
    currentMessages,
    sendMessage,
    stopStreaming,
  }
})
