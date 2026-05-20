import client from './client'
import type { BackendMessageListResponse, ChatRequest, ChatResponse, SessionStateResponse } from '../types/chat'

export function sendMessage(req: ChatRequest) {
  return client.post<ChatResponse>('/agent/chat', req)
}

export function getSessions(userTag: string) {
  return client.get<{ sessions: string[] }>('/agent/sessions', { params: { user_tag: userTag } })
}

export function getSessionMessages(sessionId: string) {
  return client.get<BackendMessageListResponse>(`/agent/sessions/${sessionId}/messages`)
}

export function deleteSession(sessionId: string, userTag: string) {
  return client.delete(`/agent/sessions/${sessionId}`, { params: { user_tag: userTag } })
}

export function getSessionState(sessionId: string, userTag: string) {
  return client.get<SessionStateResponse>(`/agent/sessions/${sessionId}/state`, {
    params: { user_tag: userTag },
  })
}
