import { CheckCircle2, FileText } from 'lucide-react'
import type { DecisionReplayRecord } from '../types'
import { strategyForKey } from '../replayUtils'
import { SectionHeading, Tag } from './ReplayPrimitives'
import { isMockMode } from '../../../services/apiConfig'

export default function OriginalDecision({ record }: { record: DecisionReplayRecord }) {
  const strategy = strategyForKey(record.scenario, record.originalStrategyKey)
  const outcome = record.actualOutcome

  return (
    <section className="overflow-hidden rounded-2xl border border-slate-200/80 bg-white shadow-sm shadow-slate-200/40">
      <SectionHeading title="Original incident & outcome" subtitle="Incident context and the recorded demo decision outcome." icon={<FileText size={17} />} />
      <div className="grid gap-5 p-5 sm:p-6 lg:grid-cols-[minmax(0,1.1fr)_minmax(300px,0.9fr)]">
        <div>
          <div className="mb-3 flex flex-wrap gap-2">
            <Tag>{record.incident.id}</Tag><Tag tone="blue">{record.incident.crisisType}</Tag>
            <Tag>{record.incident.reportedAt}</Tag>
          </div>
          <h3 className="text-sm font-semibold text-slate-900">{record.incident.title}</h3>
          <p className="mt-2 text-xs leading-5 text-slate-600">{record.scenario.summary}</p>
          <div className="mt-4">
            <p className="mb-2 text-[10px] font-bold uppercase tracking-wide text-slate-400">Business constraints · demo</p>
            <div className="grid gap-2 sm:grid-cols-3">
              {record.scenario.constraints.map((constraint) => (
                <div key={constraint.id} className="rounded-lg border border-slate-100 bg-slate-50/70 p-3">
                  <p className="text-[10px] text-slate-400">{constraint.label}</p>
                  <p className="mt-1 text-[11px] font-semibold leading-4 text-slate-700">{constraint.detail}</p>
                </div>
              ))}
            </div>
          </div>
        </div>
        <div className="rounded-xl border border-emerald-100 bg-emerald-50/50 p-4">
          <div className="flex items-center justify-between gap-2">
            <p className="text-[10px] font-bold uppercase tracking-[0.1em] text-emerald-800">{isMockMode ? 'Original decision · synthetic demo' : 'Original decision · backend record'}</p>
            <CheckCircle2 size={17} className={outcome.successful ? 'text-emerald-600' : 'text-amber-600'} />
          </div>
          <h3 className="mt-2 text-sm font-semibold text-slate-900">{strategy.name}</h3>
          <p className="mt-1 text-xs leading-5 text-slate-600">{outcome.summary}</p>
          <div className="mt-4 grid grid-cols-2 gap-2">
            <Metric label="Actual cost" value={formatCurrency(outcome.additionalCost)} />
            <Metric label="Actual delivery delay" value={`${outcome.deliveryDelayDays} days`} />
            <Metric label="Actual shortage" value={`${outcome.inventoryShortageUnits.toLocaleString()} units`} />
            <Metric label="Orders affected" value={outcome.ordersAffected.toLocaleString()} />
          </div>
        </div>
      </div>
      <p className="border-t border-slate-100 px-5 py-3 text-[10px] text-slate-400 sm:px-6">{isMockMode ? 'All outcomes shown are synthetic demo examples, not verified historical business records.' : 'Original incident and outcome were supplied by the configured backend API.'}</p>
    </section>
  )
}

function Metric({ label, value }: { label: string; value: string }) {
  return <div className="rounded-lg border border-emerald-100/80 bg-white/80 p-2.5"><p className="text-[9px] text-slate-400">{label}</p><p className="mt-1 text-xs font-semibold text-slate-800">{value}</p></div>
}

function formatCurrency(value: number): string {
  return new Intl.NumberFormat('en-US', { style: 'currency', currency: 'USD', maximumFractionDigits: 0 }).format(value)
}
