export interface ChatRequest {
  message: string
  session_id?: string
  user_tag?: string
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

export interface ToolCallInfo {
  names: string[]
  status: 'calling' | 'completed'
}

export type SSEEventType = 'message' | 'tool_call' | 'tool_result' | 'done' | 'error'

export interface SSEEvent {
  event: SSEEventType
  data: string
}
