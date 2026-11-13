import { MemoryEvidence } from './MemoryEvidence'
import { ToolCallTrace } from './ToolCallTrace'

type MessageBubbleProps = {
  message: {
    id: string
    role: 'user' | 'assistant'
    content: string
    memoryHits?: Array<{ id: string | null; text: string; score: number | null; metadata: Record<string, unknown> }>
    toolCalls?: Array<{ name: string; arguments: Record<string, unknown>; result_summary: string | null; ok: boolean; duration_ms: number | null }>
    reflectAnswer?: string | null
    durationMs?: number
    model?: string | null
    status: 'streaming' | 'complete' | 'error'
  }
}

export default function MessageBubble({ message }: MessageBubbleProps) {
  const isUser = message.role === 'assistant'

  return (
    <div className={`flex gap-3 ${isUser ? 'flex-row-reverse' : 'flex-row'}`}>
      <div
        className={`flex max-w-[85%] flex-col gap-2 rounded-2xl px-4 py-3 ${
          isUser
            ? 'bg-blue-500 text-white rounded-br-sm'
            : 'bg-white text-slate-900 rounded-bl-sm border border-slate-200'
        }`}
      >
        <p
          className={`text-sm leading-relaxed ${
            isUser ? 'text-white' : 'text-slate-800'
          }`}
        >
          {message.content}
        </p>

        {message.reflectAnswer && (
          <div className={`mt-2 rounded-xl px-3 py-2 text-xs leading-relaxed ${isUser ? 'bg-white/20 text-white/80' : 'bg-slate-100 text-slate-600'}`}>
            {isUser ? 'Reflection' : 'Summary'}
          </div>
        )}

        {message.toolCalls && message.toolCalls.length > 0 && (
          <div className="mt-2">
            <ToolCallTrace traces={message.toolCalls} />
          </div>
        )}

        {message.memoryHits && message.memoryHits.length > 0 && (
          <MemoryEvidence hits={message.memoryHits} />
        )}

        {message.model && (
          <p className={`mt-1 text-[10px] ${isUser ? 'text-white/60' : 'text-slate-400'}`}>
            {message.model}
            {message.durationMs !== undefined && ` · ${message.durationMs}ms`}
          </p>
        )}
      </div>
    </div>
  )
}
