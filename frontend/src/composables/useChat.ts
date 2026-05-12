import { useChatStore } from '../stores/chat'

export function useChat() {
  const store = useChatStore()

  async function init() {
    await store.fetchSessions()
    if (!store.currentSessionId && store.sessions.length === 0) {
      store.createSession()
    }
  }

  return {
    sessions: store.sessions,
    currentSessionId: store.currentSessionId,
    messages: store.messages,
    isStreaming: store.isStreaming,
    currentMessages: store.currentMessages,
    selectSession: store.selectSession,
    createSession: store.createSession,
    deleteSession: store.deleteSession,
    sendMessage: store.sendMessage,
    stopStreaming: store.stopStreaming,
    init,
  }
}
