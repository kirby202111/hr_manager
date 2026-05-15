import client from './client'
import type { BackendMessageListResponse, ChatRequest, ChatResponse } from '../types/chat'

export function sendMessage(req: ChatRequest) {
  return client.post<ChatResponse>('/agent/chat', req)
}

export function getSessions(userTag: string) {
  return client.get<{ sessions: string[] }>('/agent/sessions', { params: { user_tag: userTag } })
}

export function getSessionMessages(sessionId: string) {
  return client.get<BackendMessageListResponse>(`/agent/sessions/${sessionId}/messages`)
}

export function deleteSession(sessionId: string) {
  return client.delete(`/agent/sessions/${sessionId}`)
}
