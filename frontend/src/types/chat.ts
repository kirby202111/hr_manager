export interface ChatRequest {
  message: string
  session_id?: string
}

export interface ChatResponse {
  session_id: string
  reply: string
}

export interface ChatMessage {
  id: string
  role: 'user' | 'assistant'
  content: string
  timestamp: number
  toolCalls?: ToolCallInfo[]
  isStreaming?: boolean
  isError?: boolean
}

export interface ToolCallInfo {
  names: string[]
  status: 'calling' | 'completed'
}

export type SSEEventType = 'message' | 'tool_call' | 'tool_result' | 'done' | 'error'

export interface SSEEvent {
  event: SSEEventType
  data: string
}
