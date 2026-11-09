import { AlertCircle, Check, CircleDollarSign, Clock3, PackageOpen, RefreshCw, ShieldAlert } from 'lucide-react'
import type { ReactNode } from 'react'
import type { RecoveryStrategy } from '../../types/simulation'
import { formatCurrency } from './decisionUtils'
import { isMockMode } from '../../services/apiConfig'

export function LoadingState() {
  return (
    <div className="space-y-5" aria-label="Loading decision report">
      <div className="h-28 animate-pulse rounded-2xl bg-slate-200/70" />
      <div className="grid gap-5 lg:grid-cols-2">
        <div className="h-80 animate-pulse rounded-2xl bg-slate-200/70" />
        <div className="h-80 animate-pulse rounded-2xl bg-slate-200/70" />
      </div>
      <div className="h-64 animate-pulse rounded-2xl bg-slate-200/70" />
    </div>
  )
}

export function EmptyState() {
  return (
    <div className="flex min-h-[320px] flex-col items-center justify-center rounded-2xl border border-dashed border-slate-300 bg-white p-8 text-center">
      <PackageOpen className="mb-3 text-slate-400" size={30} />
      <h2 className="font-semibold text-slate-900">No incidents available</h2>
      <p className="mt-2 text-sm text-slate-500">{isMockMode ? 'There are no illustrative decision reports to display.' : 'The API returned no decision reports.'}</p>
    </div>
  )
}

export function ErrorState({ onRetry }: { onRetry: () => void }) {
  return (
    <div className="flex min-h-[320px] flex-col items-center justify-center rounded-2xl border border-rose-200 bg-white p-8 text-center">
      <AlertCircle className="mb-3 text-rose-500" size={28} />
      <h2 className="font-semibold text-slate-900">Decision report unavailable</h2>
      <p className="mt-2 max-w-md text-sm leading-6 text-slate-500">Decision data could not be loaded. Please try again.</p>
      <button type="button" onClick={onRetry} className="mt-5 inline-flex items-center gap-2 rounded-lg bg-slate-900 px-4 py-2 text-sm font-medium text-white transition hover:bg-slate-700">
        <RefreshCw size={15} />Try again
      </button>
    </div>
  )
}

export function SectionHeader({
  icon,
  title,
  description,
  tag,
}: {
  icon: ReactNode
  title: string
  description: string
  tag?: string
}) {
  return (
    <div className="flex flex-wrap items-start justify-between gap-3 border-b border-slate-100 px-5 py-4 sm:px-6">
      <div className="flex items-start gap-3">
        <span className="mt-0.5 flex size-9 shrink-0 items-center justify-center rounded-xl bg-blue-50 text-blue-600">{icon}</span>
        <div>
          <h2 className="text-sm font-semibold text-slate-900">{title}</h2>
          <p className="mt-1 text-xs leading-5 text-slate-500">{description}</p>
        </div>
      </div>
      {tag && <span className="rounded-full border border-blue-200 bg-blue-50 px-2.5 py-1 text-[9px] font-bold uppercase tracking-[0.1em] text-blue-700">{tag}</span>}
    </div>
  )
}

export function InfoList({
  title,
  items,
  color,
  icon,
}: {
  title: string
  items: string[]
  color: string
  icon: ReactNode
}) {
  return (
    <div>
      <h3 className="mb-3 flex items-center gap-2 text-xs font-semibold text-slate-800"><span className={color}>{icon}</span>{title}</h3>
      <ul className="space-y-2.5">
        {items.map((item) => <li key={item} className="flex gap-2 text-[11px] leading-5 text-slate-600"><Check size={13} className={`mt-1 shrink-0 ${color}`} />{item}</li>)}
      </ul>
    </div>
  )
}

export function Metric({ label, value, icon }: { label: string; value: string; icon: ReactNode }) {
  return (
    <div className="rounded-lg border border-slate-100 bg-white p-3">
      <div className="flex items-center gap-1.5 text-slate-400">{icon}<p className="text-[9px] leading-4">{label}</p></div>
      <p className="mt-1 text-xs font-semibold text-slate-800">{value}</p>
    </div>
  )
}

export function StrategyMetrics({ strategy }: { strategy: RecoveryStrategy }) {
  return (
    <div className="grid grid-cols-2 gap-3">
      <Metric label="Estimated additional cost" value={formatCurrency(strategy.additionalCost)} icon={<CircleDollarSign size={15} />} />
      <Metric label="Expected delivery time" value={`${strategy.deliveryDelayDays} days`} icon={<Clock3 size={15} />} />
       <Metric label="Projected shortage" value={strategy.projectedShortageUnits == null ? 'Unavailable' : `${strategy.projectedShortageUnits.toLocaleString()} units`} icon={<PackageOpen size={15} />} />
      <Metric label="Risk level" value={strategy.riskLevel} icon={<ShieldAlert size={15} />} />
    </div>
  )
}
