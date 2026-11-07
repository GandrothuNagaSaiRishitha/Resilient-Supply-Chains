import { Clock3 } from 'lucide-react'
import type { HistoricalIncidentMemory } from '../../types/memory'
import { isMockMode } from '../../services/apiConfig'

function formatDate(date: string): string {
  return new Intl.DateTimeFormat('en-US', { month: 'short', day: 'numeric', year: 'numeric' }).format(new Date(`${date}T00:00:00`))
}

function outcomeClass(outcome: HistoricalIncidentMemory['outcome']): string {
  return outcome === 'Successful'
    ? 'bg-emerald-50 text-emerald-700 ring-emerald-600/15'
    : 'bg-amber-50 text-amber-700 ring-amber-600/15'
}

export default function IncidentTimeline({
  memories,
  searching,
  onOpen,
}: {
  memories: HistoricalIncidentMemory[]
  searching: boolean
  onOpen: (id: string) => void
}) {
  return (
    <section className="overflow-hidden rounded-2xl border border-slate-200/80 bg-white shadow-sm shadow-slate-200/40">
      <div className="flex flex-wrap items-start justify-between gap-3 border-b border-slate-100 px-5 py-4 sm:px-6">
        <div className="flex items-start gap-3">
          <span className="mt-0.5 flex size-9 items-center justify-center rounded-xl bg-blue-50 text-blue-600"><Clock3 size={18} /></span>
          <div>
            <h2 className="text-sm font-semibold text-slate-900">Incident memory timeline</h2>
            <p className="mt-1 text-xs text-slate-500">{isMockMode ? 'Synthetic decisions and illustrative outcomes' : 'Incident decisions and reported outcomes'}</p>
          </div>
        </div>
        <span className="rounded-full bg-slate-100 px-2.5 py-1 text-[10px] font-semibold text-slate-500">{memories.length} records</span>
      </div>
      <div className="max-h-[560px] overflow-y-auto p-5 sm:p-6">
        {searching ? (
          <p className="py-8 text-center text-xs text-slate-400">Filtering illustrative records…</p>
        ) : memories.length === 0 ? (
          <p className="py-8 text-center text-xs text-slate-500">No records match these filters.</p>
        ) : (
          <div className="relative space-y-4 before:absolute before:bottom-4 before:left-[15px] before:top-4 before:w-px before:bg-slate-200">
            {memories.map((memory) => (
              <article key={memory.id} className="relative pl-9">
                <span className="absolute left-[9px] top-1.5 z-10 size-3.5 rounded-full border-[3px] border-blue-100 bg-blue-500" />
                <button type="button" onClick={() => onOpen(memory.id)} className="w-full rounded-xl border border-slate-100 bg-slate-50/70 p-3 text-left transition hover:border-blue-200 hover:bg-white">
                  <div className="flex flex-wrap items-center justify-between gap-2">
                    <span className="text-[10px] font-semibold text-slate-400">{formatDate(memory.incidentDate)}</span>
                    <span className={`rounded-full px-2 py-0.5 text-[9px] font-semibold ${outcomeClass(memory.outcome)}`}>{memory.outcome}</span>
                  </div>
                  <h3 className="mt-1.5 text-xs font-semibold text-slate-800">{memory.title}</h3>
                  <p className="mt-1 text-[10px] text-slate-500">{memory.id} · {memory.crisisType} · {memory.supplier}</p>
                  <p className="mt-2 text-[11px] leading-5 text-slate-600"><span className="font-semibold">Decision: </span>{memory.decisionTaken}</p>
                  <p className="mt-1 text-[11px] leading-5 text-slate-500">{memory.actualOutcome}</p>
                </button>
              </article>
            ))}
          </div>
        )}
      </div>
    </section>
  )
}
