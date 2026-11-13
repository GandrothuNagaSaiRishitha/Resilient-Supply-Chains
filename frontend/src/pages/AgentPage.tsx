import { useAgent } from '../hooks/useAgent'
import { isMockMode } from '../services/apiConfig'
import AgentChat from '../components/agent/AgentChat'
import ConversationList from '../components/agent/ConversationList'

export default function AgentPage() {
  const agent = useAgent()

  return (
    <section className="mx-auto max-w-[1440px] space-y-5">
      <header className="flex flex-col justify-between gap-2 sm:flex-row sm:items-end">
        <div>
          <p className="text-[10px] font-bold uppercase tracking-[0.16em] text-blue-600">
            AI agent
          </p>
          <h1 className="mt-1 text-2xl font-semibold tracking-tight text-slate-900">Agent Chat</h1>
          <p className="mt-1 text-xs text-slate-500">
            {isMockMode
              ? 'The AI agent requires API mode. Configure VITE_DATA_SOURCE=api and connect to the backend.'
              : 'Ask questions about suppliers, orders, shipments, and inventory. Hindsight memory is used when relevant.'}
          </p>
        </div>
        <span className="w-fit rounded-full border border-emerald-200 bg-emerald-50 px-3 py-1.5 text-[10px] font-semibold text-emerald-700">
          {isMockMode ? 'Mock data source' : 'Backend API data'}
        </span>
      </header>

      {isMockMode && (
        <div className="flex min-h-[400px] flex-col items-center justify-center rounded-2xl border border-amber-200 bg-amber-50 p-8 text-center">
          <p className="text-sm text-amber-800">
            Switch to API mode ({'VITE_DATA_SOURCE=api'}) to use the AI agent with real backend data
          </p>
        </div>
      )}

      {!isMockMode && (
        <div className="grid gap-5 lg:grid-cols-[280px_1fr]">
          <aside className="flex flex-col gap-3">
            <ConversationList
              conversations={agent.conversations}
              loading={agent.conversationsLoading}
              currentId={agent.currentConversationId}
              onSelect={agent.selectConversation}
              onNew={agent.startNewConversation}
            />
          </aside>

          <AgentChat
            messages={agent.messages}
            currentConversationId={agent.currentConversationId}
            loading={agent.loading}
            sending={agent.sending}
            error={agent.error}
            runs={agent.runs}
            runsLoading={agent.runsLoading}
            onSend={agent.sendMessage}
            onCancel={agent.cancelMessage}
            onRetry={agent.retry}
            onClearError={agent.clearError}
            startNewConversation={agent.startNewConversation}
          />
        </div>
      )}
    </section>
  )
}
