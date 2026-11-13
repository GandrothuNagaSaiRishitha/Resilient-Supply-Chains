import type { ChatMessage, ChatRequest } from './api'

export interface MemoryHit {
  id: string | null
  text: string
  type: string | null
  score: number | null
  metadata: Record<string, unknown>
}

export interface ToolCallTrace {
  name: string
  arguments: Record<string, unknown>
  result_summary: string | null
  ok: boolean
  duration_ms: number | null
}

export interface ChatResponse {
  conversation_id: string
  run_id: string
  answer: string
  memory_enabled: boolean
  memory_hits: MemoryHit[]
  reflect_answer: string | null
  tool_calls: ToolCallTrace[]
  evidence: Record<string, unknown>
  model: string | null
  duration_ms: number
}

export interface ChatRequest {
  message: string
  conversation_id: string | null
  memory_enabled: boolean
  new_conversation: boolean
}

export interface AgentRunSummary {
  id: string
  conversation_id: string | null
  agent: string
  question: string
  answer: string | null
  status: string
  memory_enabled: boolean
  model: string | null
  duration_ms: number | null
  tool_call_count: number
  memory_hit_count: number
  created_at: string | null
}

export interface AgentRunDetail {
  id: string
  conversation_id: string | null
  question: string
  answer: string | null
  status: string
  memory_enabled: boolean
  tool_calls: unknown[]
  evidence: Record<string, unknown>
  model: string | null
  duration_ms: number | null
  error: string | null
  created_at: string | null
}

export interface ConversationSummary {
  id: string
  title: string
  memory_enabled: boolean
  created_at: string | null
  updated_at: string | null
}

export interface ConversationDetail {
  id: string
  title: string
  memory_enabled: boolean
  messages: Array<{
    id: string
    role: string
    content: string
    created_at: string | null
  }>
}

export interface AgentServiceState {
  dataSource: 'mock' | 'api'
}

export type ChatMessage = {
  id: string
  role: 'user' | 'assistant'
  content: string
  memoryHits?: MemoryHit[]
  toolCalls?: ToolCallTrace[]
  reflectAnswer?: string | null
  durationMs?: number
  model?: string | null
  status: 'streaming' | 'complete' | 'error'
}
