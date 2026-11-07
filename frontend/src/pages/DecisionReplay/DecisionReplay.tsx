import { AlertCircle, LoaderCircle, RotateCcw, Sparkles } from 'lucide-react'
import IncidentSelector from './components/IncidentSelector'
import MemoryEvidence from './components/MemoryEvidence'
import MemoryFreeResult from './components/MemoryFreeResult'
import MemoryInformedResult from './components/MemoryInformedResult'
import OriginalDecision from './components/OriginalDecision'
import ReplayComparison from './components/ReplayComparison'
import ReplayExplanation from './components/ReplayExplanation'
import { DemoBadge } from './components/ReplayPrimitives'
import { useDecisionReplay } from './hooks/useDecisionReplay'
import { isMockMode } from '../../services/apiConfig'

export default function DecisionReplay() {
  const replay = useDecisionReplay()
  return (
    <div className="mx-auto max-w-[1440px] space-y-5">
      <header className="flex flex-col justify-between gap-3 sm:flex-row sm:items-end">
        <div>
          <p className="mb-1 text-[10px] font-bold uppercase tracking-[0.16em] text-blue-600">Decision intelligence</p>
          <h1 className="text-2xl font-semibold tracking-tight text-slate-900 sm:text-[28px]">Decision Replay Lab</h1>
          <p className="mt-1.5 text-sm text-slate-500">Explore how historical decision-outcome examples may inform a future crisis response.</p>
        </div>
        <DemoBadge>{isMockMode ? 'Illustrative demo data' : 'Backend API data'}</DemoBadge>
      </header>

      <IncidentSelector
        incidents={replay.incidents}
        value={replay.incidentId}
        disabled={replay.loading}
        onChange={replay.selectIncident}
      />

      {replay.loading ? (
        <div className="space-y-5" role="status" aria-label="Loading decision replay">
          <div className="h-52 animate-pulse rounded-2xl bg-slate-200/70" />
          <div className="grid gap-5 lg:grid-cols-2"><div className="h-64 animate-pulse rounded-2xl bg-slate-200/70" /><div className="h-64 animate-pulse rounded-2xl bg-slate-200/70" /></div>
        </div>
      ) : replay.error ? (
        <div role="alert" className="flex flex-col items-center rounded-2xl border border-rose-200 bg-white p-8 text-center">
          <AlertCircle size={26} className="text-rose-500" />
          <h2 className="mt-3 text-sm font-semibold text-slate-900">Decision replay unavailable</h2>
          <p className="mt-2 text-xs text-slate-500">{isMockMode ? 'Illustrative demo data could not be loaded or replayed.' : 'Decision replay data could not be loaded from the backend.'}</p>
          <button type="button" onClick={replay.retry} className="mt-4 inline-flex items-center gap-2 rounded-lg bg-slate-900 px-4 py-2 text-xs font-semibold text-white hover:bg-slate-700"><RotateCcw size={14} />Try again</button>
        </div>
      ) : replay.record ? (
        <>
          <OriginalDecision record={replay.record} />
          <div className="flex flex-col justify-between gap-3 sm:flex-row sm:items-center">
            <div className="flex items-start gap-2">
              <Sparkles size={16} className="mt-0.5 shrink-0 text-blue-600" />
              <div><h2 className="text-sm font-semibold text-slate-900">Compare replay scenarios</h2><p className="mt-1 text-xs text-slate-500">{isMockMode ? 'Fixed, illustrative demo recommendations—not live AI output.' : 'Compare both replay results returned by the configured backend.'}</p></div>
            </div>
            <button type="button" onClick={replay.replayIncident} disabled={replay.replaying} className="inline-flex items-center justify-center gap-2 rounded-lg bg-blue-600 px-4 py-2.5 text-xs font-semibold text-white shadow-sm shadow-blue-600/20 transition hover:bg-blue-700 disabled:cursor-not-allowed disabled:opacity-60">
              {replay.replaying ? <LoaderCircle size={15} className="animate-spin" /> : <RotateCcw size={15} />}
              {replay.replaying ? (isMockMode ? 'Refreshing demo replay...' : 'Running replay...') : 'Replay Incident'}
            </button>
          </div>
          {replay.replayMessage && <p role="status" className="rounded-lg border border-emerald-200 bg-emerald-50 p-3 text-xs leading-5 text-emerald-800">{replay.replayMessage}</p>}
          <div className="grid gap-5 xl:grid-cols-2">
            <MemoryFreeResult record={replay.record} />
            <MemoryInformedResult record={replay.record} />
          </div>
          <ReplayComparison record={replay.record} />
          <MemoryEvidence evidence={replay.record.historicalEvidence} />
          <ReplayExplanation record={replay.record} />
        </>
      ) : (
        <div className="rounded-2xl border border-dashed border-slate-300 bg-white p-8 text-center text-sm text-slate-500">No incident is available for replay.</div>
      )}
    </div>
  )
}
