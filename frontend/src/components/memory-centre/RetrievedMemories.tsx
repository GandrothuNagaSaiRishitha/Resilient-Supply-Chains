import { Brain, ChevronDown, Eye } from 'lucide-react'
import type { HistoricalIncidentMemory } from '../../types/memory'
import type { CrisisType } from '../../types/crisisReport'
import { isMockMode } from '../../services/apiConfig'

function formatDate(date: string): string {
  return new Intl.DateTimeFormat('en-US', { month: 'short', day: 'numeric', year: 'numeric' }).format(new Date(`${date}T00:00:00`))
}

function MemoryCard({
  memory,
  onOpen,
}: {
  memory: HistoricalIncidentMemory
  onOpen: (id: string) => void
}) {
  const outcomeStyle = memory.outcome === 'Successful'
    ? 'bg-emerald-50 text-emerald-700 ring-emerald-600/15'
    : 'bg-amber-50 text-amber-700 ring-amber-600/15'
  return (
    <article className="rounded-xl border border-slate-200/80 bg-white p-4 transition hover:border-blue-200 hover:shadow-sm">
      <div className="flex flex-wrap items-start justify-between gap-2">
        <div>
          <p className="text-xs font-semibold text-slate-800">{memory.id}</p>
          <p className="mt-1 text-[10px] text-slate-400">{formatDate(memory.incidentDate)} · {memory.crisisType}</p>
        </div>
        <span className={`rounded-full px-2.5 py-1 text-[9px] font-bold uppercase tracking-wide ring-1 ring-inset ${outcomeStyle}`}>{memory.outcome}{isMockMode ? ' · demo' : ''}</span>
      </div>
      <h3 className="mt-3 text-xs font-semibold leading-5 text-slate-800">{memory.title}</h3>
      <p className="mt-1 text-[10px] text-slate-500">Supplier: {memory.supplier}</p>
      <div className="mt-3 space-y-2 border-t border-slate-100 pt-3">
        <p className="text-[11px] leading-5 text-slate-600"><span className="font-semibold text-slate-700">Why relevant: </span>{isMockMode ? 'Same crisis type; shown as an illustrative historical comparison.' : 'Returned by the configured backend for the selected crisis context.'}</p>
        <p className="text-[11px] leading-5 text-slate-600"><span className="font-semibold text-slate-700">Previous decision: </span>{memory.decisionTaken}</p>
        <p className="text-[11px] leading-5 text-slate-600"><span className="font-semibold text-slate-700">Outcome: </span>{memory.actualOutcome}</p>
        <p className="text-[11px] leading-5 text-slate-600"><span className="font-semibold text-slate-700">Lesson: </span>{memory.lessonLearned}</p>
      </div>
      <button type="button" onClick={() => onOpen(memory.id)} className="mt-3 inline-flex items-center gap-1.5 text-[11px] font-semibold text-blue-700 transition hover:text-blue-900">
        <Eye size={14} />View memory detail
      </button>
    </article>
  )
}

export default function RetrievedMemories({
  memories,
  crisisTypes,
  selectedCrisisType,
  searching,
  onCrisisTypeChange,
  onOpen,
}: {
  memories: HistoricalIncidentMemory[]
  crisisTypes: CrisisType[]
  selectedCrisisType: CrisisType | ''
  searching: boolean
  onCrisisTypeChange: (crisisType: CrisisType | '') => void
  onOpen: (id: string) => void
}) {
  return (
    <section className="overflow-hidden rounded-2xl border border-slate-200/80 bg-white shadow-sm shadow-slate-200/40">
      <div className="flex flex-wrap items-start justify-between gap-3 border-b border-slate-100 px-5 py-4 sm:px-6">
        <div className="flex items-start gap-3">
          <span className="mt-0.5 flex size-9 items-center justify-center rounded-xl bg-violet-50 text-violet-600"><Brain size={18} /></span>
          <div>
            <h2 className="text-sm font-semibold text-slate-900">Retrieved memories</h2>
            <p className="mt-1 text-xs text-slate-500">{isMockMode ? 'Relevant illustrative records · no live retrieval' : 'Records returned by the configured backend'}</p>
          </div>
        </div>
        <span className="rounded-full border border-violet-100 bg-violet-50 px-2.5 py-1 text-[9px] font-semibold uppercase tracking-wide text-violet-700">{isMockMode ? 'Demo only' : 'API results'}</span>
      </div>
      <div className="border-b border-slate-100 bg-slate-50/50 px-5 py-3 sm:px-6">
        <label htmlFor="current-crisis" className="mb-1.5 block text-[10px] font-semibold text-slate-500">Current crisis context</label>
        <div className="relative">
          <select
            id="current-crisis"
            value={selectedCrisisType}
            onChange={(event) => onCrisisTypeChange(event.target.value as CrisisType | '')}
            className="w-full appearance-none rounded-lg border border-slate-200 bg-white px-3 py-2.5 pr-9 text-xs text-slate-700 outline-none transition focus:border-blue-400 focus:ring-4 focus:ring-blue-500/10"
          >
            <option value="">All crisis types</option>
            {crisisTypes.map((type) => <option key={type} value={type}>{type}</option>)}
          </select>
          <ChevronDown size={14} className="pointer-events-none absolute right-3 top-1/2 -translate-y-1/2 text-slate-400" />
        </div>
        <p className="mt-1.5 text-[10px] leading-4 text-slate-400">{isMockMode ? 'Matching crisis types are shown as relevant examples from this local demo dataset.' : 'Matching crisis types are returned by the configured backend service.'}</p>
      </div>
      <div className="max-h-[480px] space-y-3 overflow-y-auto p-5 sm:p-6">
        {searching ? (
          <p className="py-8 text-center text-xs text-slate-400">{isMockMode ? 'Loading demo examples…' : 'Loading memory results…'}</p>
        ) : memories.length === 0 ? (
          <div className="py-8 text-center">
            <Brain size={22} className="mx-auto mb-2 text-slate-300" />
            <p className="text-xs font-medium text-slate-600">No matching records</p>
            <p className="mt-1 text-[10px] text-slate-400">{isMockMode ? 'Adjust the current crisis or filters to view other synthetic records.' : 'Adjust the current crisis or filters and try again.'}</p>
          </div>
        ) : memories.map((memory) => <MemoryCard key={memory.id} memory={memory} onOpen={onOpen} />)}
      </div>
    </section>
  )
}
