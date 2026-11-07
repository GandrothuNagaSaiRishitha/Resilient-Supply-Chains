import { AlertCircle, CheckCircle2, ThumbsDown, ThumbsUp } from 'lucide-react'
import type { DecisionAction } from '../../types/decision'
import type { RecoveryStrategy } from '../../types/simulation'
import { isMockMode } from '../../services/apiConfig'

export default function DecisionActions({
  action,
  strategy,
  explanation,
  confirmation,
  confirming,
  error,
  onAccept,
  onReject,
  onExplanationChange,
  onConfirm,
}: {
  action: DecisionAction | null
  strategy: RecoveryStrategy | null
  explanation: string
  confirmation: string | null
  confirming: boolean
  error: boolean
  onAccept: () => void
  onReject: () => void
  onExplanationChange: (value: string) => void
  onConfirm: () => void
}) {
  return (
    <section className="overflow-hidden rounded-2xl border border-slate-200/80 bg-white shadow-sm shadow-slate-200/40">
      <div className="flex flex-wrap items-start justify-between gap-3 border-b border-slate-100 px-5 py-4 sm:px-6">
        <div>
          <h2 className="text-sm font-semibold text-slate-900">Decision actions</h2>
          <p className="mt-1 text-xs text-slate-500">{isMockMode ? 'Record a choice for this demo incident. No choice is sent to a backend.' : 'Record the decision for this incident through the configured backend API.'}</p>
        </div>
        <span className="rounded-full border border-blue-200 bg-blue-50 px-2.5 py-1 text-[9px] font-bold uppercase tracking-[0.1em] text-blue-700">{isMockMode ? 'Demo only' : 'API action'}</span>
      </div>
      <div className="grid gap-5 p-5 lg:grid-cols-[minmax(0,1fr)_minmax(280px,0.8fr)] sm:p-6">
        <div>
          <p className="mb-2 text-xs font-semibold text-slate-700">Choose an action</p>
          <div className="flex flex-col gap-2 sm:flex-row">
            <button type="button" onClick={onAccept} aria-pressed={action === 'accepted'} className={`inline-flex items-center justify-center gap-2 rounded-lg border px-4 py-2.5 text-xs font-semibold transition ${action === 'accepted' ? 'border-emerald-500 bg-emerald-50 text-emerald-800' : 'border-slate-200 bg-white text-slate-700 hover:bg-slate-50'}`}>
              <ThumbsUp size={15} />Accept Recommendation
            </button>
            <button type="button" onClick={onReject} aria-pressed={action === 'rejected'} className={`inline-flex items-center justify-center gap-2 rounded-lg border px-4 py-2.5 text-xs font-semibold transition ${action === 'rejected' ? 'border-rose-400 bg-rose-50 text-rose-800' : 'border-slate-200 bg-white text-slate-700 hover:bg-slate-50'}`}>
              <ThumbsDown size={15} />Reject Recommendation
            </button>
          </div>
          <label htmlFor="decision-explanation" className="mb-1.5 mt-4 block text-xs font-semibold text-slate-700">
            Decision explanation <span className="font-normal text-slate-400">(optional)</span>
          </label>
          <textarea
            id="decision-explanation"
            className="w-full rounded-lg border border-slate-200 bg-white px-3 py-2.5 text-sm text-slate-800 outline-none transition placeholder:text-slate-400 focus:border-blue-400 focus:ring-4 focus:ring-blue-500/10 min-h-20 resize-y"
            value={explanation}
            onChange={(event) => onExplanationChange(event.target.value)}
            placeholder="Add context for accepting, rejecting, or choosing an alternative..."
            rows={3}
          />
        </div>
        <div className="flex flex-col justify-between rounded-xl border border-slate-100 bg-slate-50/70 p-4">
          <div>
            <p className="text-[10px] font-bold uppercase tracking-[0.12em] text-slate-400">Current selection</p>
            <p className="mt-2 text-sm font-semibold text-slate-800">
              {action === 'rejected' ? 'Recommendation rejected' : strategy?.name ?? 'No action selected'}
            </p>
            {action === 'alternative' && <p className="mt-1 text-[10px] text-blue-700">Alternative strategy selected</p>}
            <p className="mt-2 text-[11px] leading-5 text-slate-500">
              {action ? (isMockMode ? 'Confirm to display a demo reference. This does not save a real decision.' : 'Confirm to submit this decision to the configured backend.') : 'Accept or reject the recommendation, or select an alternative above.'}
            </p>
          </div>
          <button type="button" onClick={onConfirm} disabled={!action || confirming} className="mt-4 inline-flex items-center justify-center gap-2 rounded-lg bg-blue-600 px-4 py-2.5 text-xs font-semibold text-white transition hover:bg-blue-700 disabled:cursor-not-allowed disabled:opacity-50">
            <CheckCircle2 size={15} />{confirming ? (isMockMode ? 'Preparing demo confirmation...' : 'Submitting decision...') : (isMockMode ? 'Confirm Demo Decision' : 'Confirm Decision')}
          </button>
        </div>
        {confirmation && (
          <div role="status" className="flex items-start gap-2 rounded-lg border border-emerald-200 bg-emerald-50 p-3 text-xs text-emerald-800 lg:col-span-2">
            <CheckCircle2 size={16} className="mt-0.5 shrink-0 text-emerald-600" />
            <span>{isMockMode ? `Demo decision confirmed · ${confirmation}. No backend decision was saved.` : `Decision submitted · ${confirmation}.`}</span>
          </div>
        )}
        {error && (
          <div role="alert" className="flex items-center gap-2 rounded-lg border border-rose-200 bg-rose-50 p-3 text-xs text-rose-800 lg:col-span-2">
            <AlertCircle size={15} />{isMockMode ? 'Could not prepare the demo decision confirmation.' : 'Could not submit the decision to the backend.'}
          </div>
        )}
      </div>
    </section>
  )
}
