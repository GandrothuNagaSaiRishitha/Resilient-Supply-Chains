import { CircleDollarSign, Clock3, ShieldAlert } from 'lucide-react'
import type { DecisionReplayRecord } from '../types'
import { formatCurrency, strategyForKey } from '../replayUtils'
import { SectionHeading } from './ReplayPrimitives'
import { isMockMode } from '../../../services/apiConfig'

export default function MemoryFreeResult({ record }: { record: DecisionReplayRecord }) {
  const strategy = strategyForKey(record.scenario, record.memoryFreeStrategyKey)
  return (
    <section className="overflow-hidden rounded-2xl border border-slate-200/80 bg-white shadow-sm shadow-slate-200/40">
      <SectionHeading icon={<CircleDollarSign size={17} />} title="Memory-free replay" subtitle={isMockMode ? 'Fixed demo baseline using the incident scenario only; no historical evidence considered.' : 'Memory-free result returned by the configured backend API.'} />
      <div className="p-5 sm:p-6">
        <p className="text-[10px] font-bold uppercase tracking-[0.12em] text-slate-400">{isMockMode ? 'Illustrative recommendation' : 'Recommendation'}</p>
        <h3 className="mt-1 text-lg font-semibold text-slate-900">{strategy.name}</h3>
        <p className="mt-2 text-xs leading-5 text-slate-600">{strategy.summary}</p>
        <div className="mt-4 grid grid-cols-2 gap-2">
          <Metric label="Estimated additional cost" value={formatCurrency(strategy.additionalCost)} icon={<CircleDollarSign size={14} />} />
          <Metric label="Expected delivery delay" value={`${strategy.deliveryDelayDays} days`} icon={<Clock3 size={14} />} />
           <Metric label="Projected shortage" value={strategy.projectedShortageUnits == null ? 'Unavailable' : `${strategy.projectedShortageUnits.toLocaleString()} units`} icon={<ShieldAlert size={14} />} />
          <Metric label="Risk level" value={strategy.riskLevel} icon={<ShieldAlert size={14} />} />
        </div>
        <p className="mt-4 rounded-lg bg-slate-50 p-3 text-[11px] leading-5 text-slate-600">{strategy.tradeOff}</p>
      </div>
    </section>
  )
}

function Metric({ label, value, icon }: { label: string; value: string; icon: React.ReactNode }) {
  return <div className="rounded-lg border border-slate-100 bg-slate-50/60 p-3"><div className="flex items-center gap-1.5 text-slate-400">{icon}<p className="text-[9px]">{label}</p></div><p className="mt-1 text-xs font-semibold text-slate-800">{value}</p></div>
}
