import { Plus, RotateCcw } from 'lucide-react'
import { NavLink } from 'react-router-dom'

type Conversation = {
  id: string
  title: string
  memory_enabled: boolean
  updated_at: string | null
}

type ConversationListProps = {
  conversations: Conversation[]
  loading: boolean
  onSelect: (id: string) => void
  onNew: () => void
}

export default function ConversationList({
  conversations,
  loading,
  onSelect,
  onNew,
}: ConversationListProps) {
  return (
    <div className="flex flex-col gap-3 rounded-xl border border-slate-200 bg-white p-4">
      <div className="flex items-center gap-2 border-b border-slate-100 pb-3">
        <span className="text-[10px] font-bold uppercase tracking-[0.14em] text-slate-500">
          Conversations
        </span>
        <button
          type="button"
          onClick={onNew}
          className="flex items-center gap-1.5 rounded-lg px-2.5 py-1.5 text-xs font-medium text-slate-700 transition hover:bg-slate-100"
        >
          <Plus size={14} /> New
        </button>
      </div>

      {loading ? (
        <div className="flex h-24 flex-col items-center justify-center gap-2 animate-pulse">
          <RotateCcw size={16} className="text-slate-400" />
          <span className="text-xs text-slate-500">Loading conversations…</span>
        </div>
      ) : conversations.length === 0 ? (
        <div className="flex h-24 flex-col items-center justify-center gap-2">
          <span className="text-xs text-slate-400">No conversations yet</span>
        </div>
      ) : (
        <nav className="space-y-1" aria-label="Conversations">
          {conversations.map((conv) => (
            <NavLink
              key={conv.id}
              to={`/agent/${conv.id}`}
              onClick={() => onSelect(conv.id)}
              className={({ isActive }) =>
                `flex items-center gap-2 rounded-lg px-3 py-2.5 text-[12px] transition ${
                  isActive
                    ? 'bg-blue-500/15 text-blue-600 ring-1 ring-inset ring-blue-400/20'
                    : 'text-slate-600 hover:bg-slate-50 hover:text-slate-900'
                }`
              }
            >
              <span className="flex-1 truncate">{conv.title}</span>
              {conv.memory_enabled && (
                <span className="w-1.5 h-1.5 rounded-full bg-emerald-500" />
              )}
            </NavLink>
          ))}
        </nav>
      )}

      <p className="mt-auto pt-3 text-[10px] leading-4 text-slate-400">
        Green dot indicates Hindsight memory is enabled for the conversation.
      </p>
    </div>
  )
}

