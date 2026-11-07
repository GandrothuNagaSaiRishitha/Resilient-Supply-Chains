import type { RecoveryStrategy } from '../../types/simulation'
import { formatCurrency } from './decisionUtils'
import { isMockMode } from '../../services/apiConfig'

export function ComparisonColumn({
  title,
  strategy,
  explanation,
  badge,
}: {
  title: string
  strategy: RecoveryStrategy
  explanation: string
  badge: string
}) {
  return (
    <div className="rounded-xl border border-slate-200 bg-slate-50/70 p-4">
      <div className="flex flex-wrap items-center justify-between gap-2">
        <h3 className="text-xs font-semibold text-slate-800">{title}</h3>
        <span className="rounded-full bg-white px-2 py-1 text-[9px] font-semibold text-slate-500 ring-1 ring-slate-200">{badge}</span>
      </div>
      <p className="mt-4 text-[10px] font-semibold uppercase tracking-wide text-slate-400">{isMockMode ? 'Illustrative recommendation' : 'Recommendation'}</p>
      <p className="mt-1 text-sm font-semibold text-slate-900">{strategy.name}</p>
      <div className="mt-3 flex flex-wrap gap-x-4 gap-y-1 text-[10px] text-slate-500">
        <span>{formatCurrency(strategy.additionalCost)} cost</span><span>{strategy.deliveryDelayDays} days</span>
      </div>
      <p className="mt-3 border-t border-slate-200 pt-3 text-xs leading-5 text-slate-600">{explanation}</p>
    </div>
  )
}
