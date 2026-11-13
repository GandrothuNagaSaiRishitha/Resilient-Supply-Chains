import { useCallback, useEffect, useRef, useState } from 'react'
import {
  sendChatMessage,
  listConversations,
  getConversation,
  listAgentRuns,
} from '../services/agentService'
import { normalizeApiError } from '../services/api'
import type {
  ChatMessage,
  ChatRequest,
  AgentRunSummary as AgentRunSummaryType,
  ConversationSummary,
} from '../types/agent'

const initialConversation: ChatMessage[] = []

export function useAgent() {
  const [conversations, setConversations] = useState<ConversationSummary[]>([])
  const [messages, setMessages] = useState<ChatMessage[]>(initialConversation)
  const [currentConversationId, setCurrentConversationId] = useState<string | null>(null)
  const [loading, setLoading] = useState(false)
  const [sending, setSending] = useState(false)
  const [error, setError] = useState<string | null>(null)
  const [conversationsLoading, setConversationsLoading] = useState(false)
  const [runs, setRuns] = useState<AgentRunSummaryType[]>([])
  const [runsLoading, setRunsLoading] = useState(false)

  const abortControllerRef = useRef<AbortController | null>(null)

  const clearError = useCallback(() => setError(null), [])

  const loadConversations = useCallback(async () => {
    setConversationsLoading(true)
    setError(null)
    try {
      const { conversations: convs } = await listConversations(30)
      setConversations(convs)
    } catch (err) {
      setError(normalizeApiError(err).message)
    } finally {
      setConversationsLoading(false)
    }
  }, [])

  const loadRuns = useCallback(async () => {
    setRunsLoading(true)
    try {
      const { runs } = await listAgentRuns(50)
      setRuns(runs)
    } catch (err) {
      console.warn('Failed to load agent runs', err)
    } finally {
      setRunsLoading(false)
    }
  }, [])

  useEffect(() => {
    loadConversations()
    loadRuns()
  }, [loadConversations, loadRuns])

  const selectConversation = useCallback(
    async (conversationId: string) => {
      setError(null)
      setCurrentConversationId(conversationId)
      setMessages([])
      setLoading(true)
      try {
        const detail = await getConversation(conversationId)
        setCurrentConversationId(conversationId)
        setMessages(
          detail.messages.map((m) => ({
            id: m.id,
            role: m.role as 'user' | 'assistant',
            content: m.content,
            status: 'complete' as const,
          })),
        )
      } catch (err) {
        setError(normalizeApiError(err).message)
      } finally {
        setLoading(false)
      }
    },
    [],
  )

  const startNewConversation = useCallback(() => {
    setError(null)
    setCurrentConversationId(null)
    setMessages([])
  }, [])

  const sendMessage = useCallback(
    async (text: string) => {
      if (!text.trim()) return
      setError(null)

      const userMessage: ChatMessage = {
        id: crypto.randomUUID(),
        role: 'user',
        content: text.trim(),
        status: 'complete',
      }

      setMessages((prev) => [...prev, userMessage])

      const assistantMessage: ChatMessage = {
        id: crypto.randomUUID(),
        role: 'assistant',
        content: '',
        status: 'streaming',
      }
      setMessages((prev) => [...prev, assistantMessage])

      setSending(true)
      abortControllerRef.current = new AbortController()

      try {
        const request: ChatRequest = {
          message: text.trim(),
          conversation_id: currentConversationId,
          memory_enabled: true,
          new_conversation: !currentConversationId,
        }

        const response = await sendChatMessage(request)

        const assistantMessageWithContent: ChatMessage = {
          id: assistantMessage.id,
          role: 'assistant',
          content: response.answer,
          memoryHits: response.memory_hits,
          toolCalls: response.tool_calls,
          reflectAnswer: response.reflect_answer,
          durationMs: response.duration_ms,
          model: response.model,
          status: 'complete',
        }

        setMessages((prev) =>
          prev.map((m) => (m.id === assistantMessage.id ? assistantMessageWithContent : m)),
        )

        if (response.conversation_id && !currentConversationId) {
          setCurrentConversationId(response.conversation_id)
        }

        void loadConversations()
        void loadRuns()

        return response
      } catch (err) {
        const apiError = normalizeApiError(err)
        setError(apiError.message)
        setMessages((prev) =>
          prev.map((m) =>
            m.id === assistantMessage.id
              ? { ...m, status: 'error' as const, content: apiError.message }
              : m,
          ),
        )
        throw apiError
      } finally {
        setSending(false)
        abortControllerRef.current = null
      }
    },
    [currentConversationId, loadConversations, loadRuns],
  )

  const cancelMessage = useCallback(() => {
    if (abortControllerRef.current) {
      abortControllerRef.current.abort()
      abortControllerRef.current = null
    }
    setSending(false)
  }, [])

  const retry = useCallback(() => {
    setError(null)
  }, [])

  return {
    conversations,
    messages,
    currentConversationId,
    loading,
    sending,
    error,
    conversationsLoading,
    runs,
    runsLoading,
    clearError,
    loadConversations,
    selectConversation,
    startNewConversation,
    sendMessage,
    cancelMessage,
    retry,
  }
}