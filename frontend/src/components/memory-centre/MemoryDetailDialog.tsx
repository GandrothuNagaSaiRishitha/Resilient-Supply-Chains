import { BookOpenCheck, X } from 'lucide-react'
import type { HistoricalIncidentMemory } from '../../types/memory'
import { isMockMode } from '../../services/apiConfig'

function formatDate(date: string): string {
  return new Intl.DateTimeFormat('en-US', { month: 'short', day: 'numeric', year: 'numeric' }).format(new Date(`${date}T00:00:00`))
}

export default function MemoryDetailDialog({
  open,
  memory,
  loading,
  error,
  onClose,
}: {
  open: boolean
  memory: HistoricalIncidentMemory | null
  loading: boolean
  error: string | null
  onClose: () => void
}) {
  if (!open) return null
  return (
    <div className="fixed inset-0 z-[60] flex items-center justify-center bg-slate-950/50 p-4">
      <button type="button" className="absolute inset-0 size-full cursor-default" aria-label="Close memory details" onClick={onClose} />
      <section role="dialog" aria-modal="true" aria-labelledby="memory-detail-title" className="relative z-10 max-h-[90vh] w-full max-w-2xl overflow-y-auto rounded-2xl bg-white shadow-2xl">
        <div className="flex items-start justify-between border-b border-slate-100 p-5 sm:p-6">
          <div className="flex items-start gap-3">
            <span className="flex size-9 items-center justify-center rounded-xl bg-violet-50 text-violet-600"><BookOpenCheck size={18} /></span>
            <div>
              <p className="text-[10px] font-bold uppercase tracking-[0.12em] text-violet-700">{isMockMode ? 'Synthetic illustrative record' : 'Backend memory record'}</p>
              <h2 id="memory-detail-title" className="mt-1 text-base font-semibold text-slate-900">{loading ? 'Loading memory detail' : memory?.id ?? 'Memory detail'}</h2>
            </div>
          </div>
          <button type="button" onClick={onClose} className="rounded-lg p-2 text-slate-400 transition hover:bg-slate-100 hover:text-slate-700" aria-label="Close"><X size={18} /></button>
        </div>
        <div className="p-5 sm:p-6">
          {loading && <div className="space-y-3"><div className="h-5 animate-pulse rounded bg-slate-100" /><div className="h-16 animate-pulse rounded bg-slate-100" /><div className="h-16 animate-pulse rounded bg-slate-100" /></div>}
          {error && <p role="alert" className="text-sm text-rose-700">{error}</p>}
          {memory && (
            <>
              <div className="mb-5 flex flex-wrap gap-2">
                <span className="rounded-full bg-slate-100 px-2.5 py-1 text-[10px] font-semibold text-slate-600">{formatDate(memory.incidentDate)}</span>
                <span className="rounded-full bg-blue-50 px-2.5 py-1 text-[10px] font-medium text-blue-700">{memory.crisisType}</span>
                <span className="rounded-full bg-emerald-50 px-2.5 py-1 text-[10px] font-semibold text-emerald-700">{memory.outcome}{isMockMode ? ' · demo' : ''}</span>
              </div>
              <h3 className="text-sm font-semibold text-slate-900">{memory.title}</h3>
              <p className="mt-1 text-xs text-slate-500">Supplier: {memory.supplier}</p>
              <DetailField title="Description" value={memory.description} />
              <DetailField title="Decision taken" value={memory.decisionTaken} />
              <DetailField title="Expected result" value={memory.expectedResult} />
              <DetailField title={isMockMode ? 'Illustrative actual outcome' : 'Reported actual outcome'} value={memory.actualOutcome} />
              <DetailField title="Lesson learned" value={memory.lessonLearned} />
              <p className="mt-5 rounded-lg border border-amber-100 bg-amber-50 p-3 text-[11px] leading-5 text-amber-800">{isMockMode ? 'This is a synthetic example record for interface demonstration. It is not a real stored memory or Hindsight result.' : 'This record was supplied through the backend API. The frontend does not make direct Hindsight calls.'}</p>
            </>
          )}
        </div>
      </section>
    </div>
  )
}

function DetailField({ title, value }: { title: string; value: string }) {
  return (
    <div className="mt-4">
      <h3 className="text-[10px] font-bold uppercase tracking-wide text-slate-400">{title}</h3>
      <p className="mt-1 text-xs leading-5 text-slate-600">{value}</p>
    </div>
  )
}
