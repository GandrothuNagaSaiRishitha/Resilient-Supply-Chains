import { AlertCircle, ArrowDown, ArrowUp, Check, CheckCircle2, CircleDollarSign, Compass, ShieldAlert } from 'lucide-react'
import type { RecoveryStrategyKey, SimulationScenario } from '../../types/simulation'
import { isMockMode } from '../../services/apiConfig'

function formatCurrency(value: number): string {
  return new Intl.NumberFormat('en-US', { style: 'currency', currency: 'USD', maximumFractionDigits: 0 }).format(value)
}

export default function RecommendationAndConfirmation({
  scenario,
  selectedStrategyKey,
  onConfirm,
  confirming,
  confirmation,
  confirmationError,
}: {
  scenario: SimulationScenario
  selectedStrategyKey: RecoveryStrategyKey
  onConfirm: () => void
  confirming: boolean
  confirmation: string | null
  confirmationError: boolean
}) {
  const recommendedStrategy = scenario.strategies.find(({ key }) => key === scenario.recommendedStrategyKey)
  const selectedStrategy = scenario.strategies.find(({ key }) => key === selectedStrategyKey)

  return (
    <>
      <section className="mb-5 grid gap-5 lg:grid-cols-[minmax(0,1.4fr)_minmax(300px,1fr)]">
        <div className="rounded-2xl border border-blue-100 bg-blue-50/60 p-5 sm:p-6">
          <div className="flex items-start gap-3">
            <span className="flex size-10 shrink-0 items-center justify-center rounded-xl bg-white text-blue-600 shadow-sm shadow-blue-900/5"><Compass size={20} /></span>
            <div>
              <div className="flex flex-wrap items-center gap-2">
                <h2 className="text-sm font-semibold text-slate-900">Recommended strategy</h2>
                {recommendedStrategy && <span className="rounded-full bg-blue-100 px-2 py-0.5 text-[10px] font-semibold text-blue-700">{recommendedStrategy.name}</span>}
              </div>
              <p className="mt-2 text-xs leading-6 text-slate-600">{scenario.recommendationExplanation}</p>
              {recommendedStrategy && <p className="mt-3 flex items-start gap-2 text-[11px] leading-5 text-slate-500"><ArrowDown size={14} className="mt-0.5 shrink-0 text-blue-600" />Trade-off: {recommendedStrategy.tradeOff}</p>}
            </div>
          </div>
        </div>
        <div className="rounded-2xl border border-slate-200/80 bg-white p-5 shadow-sm shadow-slate-200/40 sm:p-6">
          <div className="mb-3 flex items-center gap-2"><ShieldAlert size={18} className="text-amber-500" /><h2 className="text-sm font-semibold text-slate-900">Feasibility notes</h2></div>
          <div className="space-y-2">
            {scenario.strategies.map((strategy) => (
              <div key={strategy.key} className="flex items-start gap-2 text-[11px] leading-5 text-slate-500">
                {strategy.feasibility === 'Feasible' ? <Check size={13} className="mt-1 shrink-0 text-emerald-600" /> : <AlertCircle size={13} className="mt-1 shrink-0 text-amber-600" />}
                <span><span className="font-semibold text-slate-700">{strategy.name}:</span> {strategy.feasibilityNote}</span>
              </div>
            ))}
          </div>
        </div>
      </section>

      {confirmation && (
        <div role="status" aria-live="polite" className="mb-5 flex items-start gap-3 rounded-xl border border-emerald-200 bg-emerald-50 p-4">
          <CheckCircle2 className="mt-0.5 shrink-0 text-emerald-600" size={19} />
          <div><p className="text-sm font-semibold text-emerald-900">{isMockMode ? 'Demo choice confirmed' : 'Strategy choice confirmed'} · {confirmation}</p><p className="mt-1 text-xs leading-5 text-emerald-800">{isMockMode ? 'This is a demo confirmation only. No real decision was saved.' : 'The configured backend accepted the strategy choice.'}</p></div>
        </div>
      )}
      {confirmationError && <div role="alert" className="mb-5 flex items-center gap-2 rounded-xl border border-rose-200 bg-rose-50 p-4 text-sm text-rose-800"><AlertCircle size={17} />{isMockMode ? 'Could not prepare the demo confirmation. Please try again.' : 'Could not submit the strategy choice. Please try again.'}</div>}

      <section className="flex flex-col justify-between gap-4 rounded-2xl border border-slate-200/80 bg-white p-5 shadow-sm shadow-slate-200/40 sm:flex-row sm:items-center sm:px-6">
        <div className="flex items-start gap-3">
          <span className="flex size-9 shrink-0 items-center justify-center rounded-xl bg-slate-100 text-slate-600"><CircleDollarSign size={18} /></span>
          <div>
            <h2 className="text-sm font-semibold text-slate-900">{selectedStrategy ? `Selected: ${selectedStrategy.name}` : 'Select a strategy'}</h2>
            <p className="mt-1 text-xs text-slate-500">{selectedStrategy ? `${formatCurrency(selectedStrategy.additionalCost)} added cost · ${selectedStrategy.deliveryDelayDays} days delivery delay` : 'Choose one of the strategies above to review and confirm.'}</p>
          </div>
        </div>
        <button type="button" onClick={onConfirm} disabled={!selectedStrategy || confirming} className="inline-flex shrink-0 items-center justify-center gap-2 rounded-lg bg-blue-600 px-5 py-2.5 text-sm font-semibold text-white shadow-sm shadow-blue-600/20 transition hover:bg-blue-700 disabled:cursor-not-allowed disabled:opacity-50">
          <CheckCircle2 size={16} />{confirming ? (isMockMode ? 'Preparing demo confirmation...' : 'Submitting strategy choice...') : 'Confirm strategy'}
        </button>
      </section>
      <p className="mt-4 flex items-start gap-2 text-[11px] leading-5 text-slate-400"><ArrowUp size={13} className="mt-0.5 shrink-0" />{isMockMode ? 'All scenario values and recommendations are illustrative demo simulations, not operational data or real predictions.' : 'Scenario estimates use recorded incident, supplier, purchase-order, and inventory data. Transfer feasibility remains conditional where location and capacity data are unavailable.'}</p>
    </>
  )
}
