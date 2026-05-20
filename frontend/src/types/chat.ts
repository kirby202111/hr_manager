export interface ChatRequest {
  message: string
  session_id?: string
  user_tag?: string
}

export interface ChatResponse {
  session_id: string
  reply: string
}

export interface OnboardingCaseSummary {
  id: number
  session_id: string
  user_tag: string
  intent: string
  worker_id?: number | null
  worker_code?: string | null
  worker_name?: string | null
  employment_type?: string | null
  hire_date?: string | null
  organization_unit_id?: number | null
  organization_unit_name?: string | null
  production_line_id?: number | null
  production_line_name?: string | null
  production_team_id?: number | null
  production_team_name?: string | null
  role_title?: string | null
  target_workstation_id?: number | null
  target_workstation_name?: string | null
  collected_fields: string[]
  missing_fields: string[]
  pending_actions: string[]
  completed_actions: string[]
  risk_flags: string[]
  latest_eligibility?: {
    status?: string
    summary_reason?: string
    details?: Array<{ status?: string; message?: string }>
    checked_at?: string
  } | null
  last_agent_summary?: string | null
  is_active: boolean
  created_at: string
  updated_at: string
}

export interface SessionStateResponse {
  session_id: string
  onboarding_case?: OnboardingCaseSummary | null
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
