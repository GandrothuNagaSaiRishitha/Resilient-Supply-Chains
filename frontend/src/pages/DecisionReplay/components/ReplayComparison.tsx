import { ArrowRightLeft, Check } from 'lucide-react'
import type { DecisionReplayRecord } from '../types'
import { formatCurrency, strategyForKey } from '../replayUtils'
import { SectionHeading } from './ReplayPrimitives'
import { isMockMode } from '../../../services/apiConfig'

export default function ReplayComparison({ record }: { record: DecisionReplayRecord }) {
  const baseline = strategyForKey(record.scenario, record.memoryFreeStrategyKey)
  const memoryStatus = record.memoryStatus ?? (isMockMode ? 'available' : 'unavailable')
  const informed = memoryStatus === 'available' && record.memoryInformedStrategyKey
    ? strategyForKey(record.scenario, record.memoryInformedStrategyKey)
    : null
  const rows = [
    { label: 'Recommendation', baseline: baseline.name, informed: informed?.name ?? 'Unavailable' },
    { label: 'Estimated cost', baseline: formatCurrency(baseline.additionalCost), informed: informed ? formatCurrency(informed.additionalCost) : 'Unavailable' },
    { label: 'Delivery delay', baseline: `${baseline.deliveryDelayDays} days`, informed: informed ? `${informed.deliveryDelayDays} days` : 'Unavailable' },
     { label: 'Projected shortage', baseline: baseline.projectedShortageUnits == null ? 'Unavailable' : `${baseline.projectedShortageUnits.toLocaleString()} units`, informed: informed?.projectedShortageUnits == null ? 'Unavailable' : `${informed.projectedShortageUnits.toLocaleString()} units` },
    { label: 'Risk', baseline: baseline.riskLevel, informed: informed?.riskLevel ?? 'Unavailable' },
  ]

  return (
    <section className="overflow-hidden rounded-2xl border border-slate-200/80 bg-white shadow-sm shadow-slate-200/40">
      <SectionHeading icon={<ArrowRightLeft size={17} />} title="Replay comparison" subtitle={isMockMode ? 'Side-by-side fixed demo estimates; these are not live model outputs.' : 'Side-by-side estimates returned by the configured backend API.'} />
      <div className="overflow-x-auto">
        <table className="w-full min-w-[560px] text-left">
          <thead><tr className="border-b border-slate-100 bg-slate-50/70 text-[10px] font-bold uppercase tracking-wide text-slate-400"><th className="px-5 py-3 sm:px-6">Measure</th><th className="px-4 py-3">Memory-free</th><th className="px-4 py-3">Memory-informed</th></tr></thead>
          <tbody className="divide-y divide-slate-100">
            {rows.map((row) => <tr key={row.label} className="text-xs text-slate-600"><th className="px-5 py-3 font-medium text-slate-500 sm:px-6">{row.label}</th><td className="px-4 py-3">{row.baseline}</td><td className="px-4 py-3 font-semibold text-slate-800">{row.informed}</td></tr>)}
          </tbody>
        </table>
      </div>
      <div className="grid gap-3 p-5 sm:grid-cols-2 sm:p-6">
        <Reason title="Memory-free rationale" text={baseline.tradeOff} />
        <Reason title={informed ? 'Memory-informed change' : 'Memory-informed comparison'} text={record.comparisonExplanation} />
      </div>
    </section>
  )
}

function Reason({ title, text }: { title: string; text: string }) {
  return <div className="rounded-xl border border-slate-100 bg-slate-50/60 p-4"><h3 className="flex items-center gap-2 text-[11px] font-semibold text-slate-800"><Check size={14} className="text-blue-600" />{title}</h3><p className="mt-2 text-[11px] leading-5 text-slate-600">{text}</p></div>
}
