import { RotateCcw, Send, StopCircle, Trash2 } from "lucide-react"
import MessageBubble from "./MessageBubble"

type AgentChatProps = {
  messages: Array<{
    id: string
    role: "user" | "assistant"
    content: string
    memoryHits?: Array<{ id: string | null; text: string; score: number | null; metadata: Record<string, unknown> }>
    toolCalls?: Array<{ name: string; arguments: Record<string, unknown>; result_summary: string | null; ok: boolean; duration_ms: number | null }>
    reflectAnswer?: string | null
    durationMs?: number
    model?: string | null
    status: "streaming" | "complete" | "error"
  }>
  currentConversationId: string | null
  loading: boolean
  sending: boolean
  error: string | null
  runs: Array<{ id: string; status: string; tool_call_count: number; memory_hit_count: number; created_at: string | null }>
  onSend: (text: string) => void
  onCancel: () => void
  onRetry: () => void
  onClearError: () => void
  startNewConversation: () => void
}

export default function AgentChat({
  messages,
  currentConversationId,
  loading,
  sending,
  error,
  runs,
  onSend,
  onCancel,
  onRetry,
  onClearError,
  startNewConversation,
}: AgentChatProps) {
  return (
    <div className="flex flex-col gap-4 rounded-xl border border-slate-200 bg-white p-4 sm:p-6">
      <header className="flex items-center justify-between border-b border-slate-100 pb-3">
        <div className="flex items-center gap-2">
          <span className="text-xs font-semibold text-slate-900">Conversation</span>
          {currentConversationId && (
            <span className="text-[10px] text-slate-500">· {currentConversationId.slice(0, 8)}…</span>
          )}
        </div>
        <div className="flex items-center gap-2">
          {loading && (
            <button
              type="button"
              onClick={onCancel}
              className="flex items-center gap-1.5 rounded-lg px-2.5 py-1.5 text-xs font-medium text-slate-700 transition hover:bg-slate-100"
            >
              <StopCircle size={14} /> Cancel
            </button>
          )}
          <button
            type="button"
            onClick={startNewConversation}
            className="flex items-center gap-1.5 rounded-lg px-2.5 py-1.5 text-xs font-medium text-slate-700 transition hover:bg-slate-100"
          >
            <Trash2 size={14} /> New chat
          </button>
        </div>
      </header>

      {error && (
        <div role="alert" className="flex items-center gap-2 rounded-xl border border-rose-200 bg-rose-50 p-3">
          <span className="text-rose-500" size={16}>
            <RotateCcw />
          </span>
          <span className="text-sm text-rose-800">{error}</span>
          <button
            type="button"
            onClick={onRetry}
            className="ml-auto inline-flex items-center gap-1 rounded-lg px-2.5 py-1 text-xs font-medium text-rose-700 transition hover:bg-rose-100"
          >
            <RotateCcw size={14} /> Retry
          </button>
          <button
            type="button"
            onClick={onClearError}
            className="rounded-lg px-2.5 py-1 text-xs text-slate-500 transition hover:bg-slate-100"
          >
            Dismiss
          </button>
        </div>
      )}

      <div className="flex-1 min-h-[300px] overflow-y-auto space-y-4">
        {messages.length === 0 && !loading && !error && (
          <div className="flex h-full flex-col items-center justify-center text-center pt-16">
            <p className="text-sm text-slate-500">Start a conversation by asking about your supply chain.</p>
          </div>
        )}
        {messages.map((msg) => (
          <MessageBubble key={msg.id} message={msg} />
        ))}
        {loading && messages.length > 0 && (
          <div className="flex items-end gap-2">
            <div className="w-full max-w-[80%]">
              <div className="flex gap-2">
                <div className="flex-1 h-8 rounded-xl bg-slate-200 animate-pulse" />
                <div className="w-16 h-8 rounded-xl bg-slate-200 animate-pulse" />
              </div>
            </div>
          </div>
        )}
      </div>

      {runs.length > 0 && (
        <div className="flex flex-col gap-2">
          <h3 className="text-[10px] font-bold uppercase tracking-[0.14em] text-slate-500">Recent agent runs</h3>
          <div className="grid gap-2">
            {runs.slice(0, 5).map((run) => (
              <div key={run.id} className="flex items-center justify-between rounded-lg border border-slate-100 bg-slate-50 p-2">
                <span className="text-xs text-slate-600">{run.status}</span>
                <div className="flex items-center gap-1.5 text-[10px] text-slate-500">
                  <span>{run.tool_call_count} tools</span>
                  <span>{run.memory_hit_count} memories</span>
                </div>
              </div>
            ))
          </div>
        </div>
      )}

      <form
        onSubmit={(e) => {
          e.preventDefault()
          const input = e.currentTarget.elements.namedItem("message") as HTMLInputElement | null
          if (input?.value.trim()) {
            onSend(input.value)
            input.value = ""
          }
        }}
        className="flex items-end gap-2 rounded-xl border border-slate-200 bg-white p-3"
      >
        <input
          name="message"
          type="text"
          placeholder="Ask about suppliers, orders, shipments, inventory…"
          disabled={sending || loading}
          className="flex-1 min-w-0 bg-transparent border-0 outline-none text-sm text-slate-900 placeholder:text-slate-400"
        />
        <button
          type="submit"
          disabled={sending || loading}
          className="rounded-lg bg-slate-900 px-4 py-2.5 text-sm font-medium text-white disabled:opacity-50 disabled:pointer-events-none transition hover:bg-slate-800"
        >
          <Send size={16} />
        </button>
      </form>
    </div>
  )
}
