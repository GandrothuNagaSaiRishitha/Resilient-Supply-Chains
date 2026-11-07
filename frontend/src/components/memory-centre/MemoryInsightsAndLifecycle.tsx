import {
  Archive,
  ArrowRight,
  CircleHelp,
  Lightbulb,
  Network,
  Search,
  Sparkles,
} from 'lucide-react'
import type { LearnedInsight, MemoryLifecycleStage } from '../../types/memory'
import { isMockMode } from '../../services/apiConfig'

const insightStyles: Record<LearnedInsight['category'], string> = {
  'Recurring pattern': 'bg-violet-50 text-violet-700',
  'Successful strategy': 'bg-emerald-50 text-emerald-700',
  'Ineffective approach': 'bg-amber-50 text-amber-700',
  'Lesson learned': 'bg-blue-50 text-blue-700',
}

export function LearnedInsights({ insights }: { insights: LearnedInsight[] }) {
  return (
    <section className="mb-5">
      <div className="mb-3 flex items-center gap-2">
        <span className="flex size-8 items-center justify-center rounded-lg bg-amber-50 text-amber-600"><Lightbulb size={17} /></span>
        <div>
          <h2 className="text-sm font-semibold text-slate-900">Learned insights</h2>
          <p className="mt-0.5 text-xs text-slate-500">{isMockMode ? 'Patterns from synthetic outcomes · demo only' : 'Insights returned by the configured backend'}</p>
        </div>
      </div>
      <div className="grid gap-3 sm:grid-cols-2 xl:grid-cols-4">
        {insights.map((insight) => (
          <article key={insight.id} className="rounded-xl border border-slate-200/80 bg-white p-4">
            <div className="mb-3 flex items-center justify-between gap-2">
              <span className={`rounded-full px-2 py-1 text-[9px] font-semibold ${insightStyles[insight.category]}`}>{insight.category}</span>
              <span className="text-[9px] text-slate-400">{insight.evidenceCount} {isMockMode ? 'demo records' : 'evidence records'}</span>
            </div>
            <h3 className="text-xs font-semibold text-slate-800">{insight.title}</h3>
            <p className="mt-1.5 text-[11px] leading-5 text-slate-500">{insight.description}</p>
          </article>
        ))}
      </div>
    </section>
  )
}

function LifecycleCard({ stage, index }: { stage: MemoryLifecycleStage; index: number }) {
  const icons = { retain: Archive, recall: Search, reflect: Sparkles }
  const Icon = icons[stage.id]
  return (
    <article className="relative rounded-xl border border-slate-200/80 bg-white p-4">
      <div className="mb-3 flex items-center justify-between">
        <span className="flex size-9 items-center justify-center rounded-xl bg-blue-50 text-blue-600"><Icon size={18} /></span>
        <span className="flex size-6 items-center justify-center rounded-full bg-slate-100 text-[10px] font-bold text-slate-500">0{index + 1}</span>
      </div>
      <h3 className="text-xs font-semibold text-slate-900">{stage.title}</h3>
      <p className="mt-1.5 text-[11px] leading-5 text-slate-500">{stage.description}</p>
      <p className="mt-3 rounded-lg bg-slate-50 p-2.5 text-[10px] leading-4 text-slate-500">{stage.example}</p>
    </article>
  )
}

export function MemoryLifecycle({ lifecycle }: { lifecycle: MemoryLifecycleStage[] }) {
  return (
    <section className="rounded-2xl border border-slate-200/80 bg-slate-50/70 p-5 sm:p-6">
      <div className="mb-5 flex items-start gap-3">
        <span className="flex size-9 items-center justify-center rounded-xl bg-white text-blue-600 shadow-sm"><Network size={18} /></span>
        <div>
          <h2 className="text-sm font-semibold text-slate-900">Memory lifecycle</h2>
          <p className="mt-1 text-xs text-slate-500">{isMockMode ? 'Conceptual flow for a future memory-backed workflow—not implemented persistence.' : 'Conceptual lifecycle view; backend retention and retrieval behavior depends on its implementation.'}</p>
        </div>
      </div>
      <div className="grid gap-3 md:grid-cols-3">
        {lifecycle.map((stage, index) => (
          <div key={stage.id} className="relative">
            <LifecycleCard stage={stage} index={index} />
            {index < lifecycle.length - 1 && <ArrowRight className="absolute -right-3 top-1/2 z-10 hidden -translate-y-1/2 text-blue-300 md:block" size={18} />}
          </div>
        ))}
      </div>
      <div className="mt-4 flex items-start gap-2 rounded-lg border border-blue-100 bg-blue-50/70 p-3 text-[11px] leading-5 text-blue-800">
        <CircleHelp size={15} className="mt-0.5 shrink-0" />
        {isMockMode ? 'Real retention, recall, and reflection behavior requires backend integration. This screen does not connect to a memory system.' : 'This frontend calls the configured memory API only. No Hindsight SDK or direct browser integration is used.'}
      </div>
    </section>
  )
}
