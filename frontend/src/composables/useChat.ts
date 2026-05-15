import { useChatStore } from '../stores/chat'

export function useChat() {
  const store = useChatStore()

  async function init() {
    await store.fetchSessions()
    if (store.currentSessionId) {
      await store.selectSession(store.currentSessionId)
    } else if (store.sessions.length === 0) {
      store.createSession()
    }
  }

  return {
    sessions: store.sessions,
    currentSessionId: store.currentSessionId,
    messages: store.messages,
    userTag: store.userTag,
    isLoadingMessages: store.isLoadingMessages,
    isStreaming: store.isStreaming,
    currentMessages: store.currentMessages,
    selectSession: store.selectSession,
    createSession: store.createSession,
    deleteSession: store.deleteSession,
    sendMessage: store.sendMessage,
    stopStreaming: store.stopStreaming,
    setUserTag: store.setUserTag,
    init,
  }
}
