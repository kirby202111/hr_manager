import client from './client'
import type { ChatRequest, ChatResponse } from '../types/chat'

export function sendMessage(req: ChatRequest) {
  return client.post<ChatResponse>('/agent/chat', req)
}

export function getSessions() {
  return client.get<{ sessions: string[] }>('/agent/sessions')
}

export function deleteSession(sessionId: string) {
  return client.delete(`/agent/sessions/${sessionId}`)
}
