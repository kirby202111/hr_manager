import { fetchEventSource } from '@microsoft/fetch-event-source'
import type { ChatRequest } from '../types/chat'

export interface StreamCallbacks {
  onMessage: (text: string) => void
  onToolCall: (names: string[]) => void
  onToolResult: (names: string[]) => void
  onDone: (sessionId: string) => void
  onError: (error: string) => void
}

export function streamChat(
  request: ChatRequest,
  callbacks: StreamCallbacks,
  ctrl: AbortController,
): Promise<void> {
  const baseURL = import.meta.env.VITE_API_BASE_URL || ''
  const url = `${baseURL}/agent/chat/stream`
  let sessionId = request.session_id || ''

  return fetchEventSource(url, {
    method: 'POST',
    headers: { 'Content-Type': 'application/json' },
    body: JSON.stringify(request),
    signal: ctrl.signal,
    openWhenHidden: true,

    async onopen(response) {
      if (!response.ok) {
        throw new Error(`HTTP ${response.status}`)
      }
      const sid = response.headers.get('X-Session-ID')
      if (sid) sessionId = sid
    },

    onmessage(event) {
      switch (event.event as string) {
        case 'message':
          callbacks.onMessage(event.data)
          break
        case 'tool_call':
          callbacks.onToolCall(JSON.parse(event.data))
          break
        case 'tool_result':
          callbacks.onToolResult(JSON.parse(event.data))
          break
        case 'done':
          callbacks.onDone(sessionId)
          break
        case 'error':
          callbacks.onError(event.data)
          break
      }
    },

    onerror(err) {
      callbacks.onError(err instanceof Error ? err.message : '连接错误')
      throw err
    },
  })
}
