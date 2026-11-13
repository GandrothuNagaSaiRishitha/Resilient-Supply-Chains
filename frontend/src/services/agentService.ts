import api from './api'
import { apiEndpoints } from './apiEndpoints'
import { isMockMode } from './apiConfig'
import type { ApiResponse } from '../types/api'
import type {
  ChatRequest,
  ChatResponse,
  AgentRunSummary,
  AgentRunDetail,
  ConversationSummary,
  ConversationDetail,
} from '../types/agent'

export async function sendChatMessage(
  request: ChatRequest,
): Promise<ChatResponse> {
  if (isMockMode) {
    throw new Error(
      'The AI Agent is not available in mock data mode. Switch VITE_DATA_SOURCE to "api" and connect to the backend.',
    )
  }
  const response = await api.post<ApiResponse<ChatResponse>>(
    apiEndpoints.agentChat,
    request,
    { timeout: 600_000 },
  )
  return response.data
}

export async function listAgentRuns(
  limit = 50,
): Promise<{ count: number; runs: AgentRunSummary[] }> {
  if (isMockMode) {
    return { count: 0, runs: [] }
  }
  const response = await api.get<ApiResponse<{ count: number; runs: AgentRunSummary[] }>>(
    apiEndpoints.agentRuns,
    { params: { limit } },
  )
  return response.data
}

export async function getAgentRun(runId: string): Promise<AgentRunDetail> {
  if (isMockMode) {
    throw new Error('Agent run details are not available in mock data mode.')
  }
  const response = await api.get<ApiResponse<AgentRunDetail>>(
    apiEndpoints.agentRun(runId),
  )
  return response.data
}

export async function listConversations(
  limit = 30,
): Promise<{ count: number; conversations: ConversationSummary[] }> {
  if (isMockMode) {
    return { count: 0, conversations: [] }
  }
  const response = await api.get<ApiResponse<{ count: number; conversations: ConversationSummary[] }>>(
    apiEndpoints.agentConversations,
    { params: { limit } },
  )
  return response.data
}

export async function getConversation(
  conversationId: string,
): Promise<ConversationDetail> {
  if (isMockMode) {
    throw new Error('Conversation details are not available in mock data mode.')
  }
  const response = await api.get<ApiResponse<ConversationDetail>>(
    apiEndpoints.agentConversation(conversationId),
  )
  return response.data
}
