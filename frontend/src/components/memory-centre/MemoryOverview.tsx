import {
  AlertCircle,
  Archive,
  CheckCircle2,
  Database,
  Lightbulb,
} from 'lucide-react'
import type { MemoryOverviewStats } from '../../types/memory'
import { isMockMode } from '../../services/apiConfig'

const statsCards = [
  { key: 'totalHistoricalIncidents', label: 'Historical incidents', icon: Archive, color: 'bg-blue-50 text-blue-600' },
  { key: 'successfulStrategies', label: 'Successful strategies', icon: CheckCircle2, color: 'bg-emerald-50 text-emerald-600' },
  { key: 'ineffectiveStrategies', label: 'Ineffective strategies', icon: AlertCircle, color: 'bg-amber-50 text-amber-600' },
  { key: 'lessonsRetained', label: 'Lessons retained', icon: Lightbulb, color: 'bg-violet-50 text-violet-600' },
] as const

export function MemoryStatusNotice() {
  return (
    <div className="mb-5 flex items-start gap-3 rounded-2xl border border-amber-200 bg-amber-50/80 p-4">
      <Database size={18} className="mt-0.5 shrink-0 text-amber-700" />
      <div>
        <h2 className="text-xs font-semibold text-amber-900">{isMockMode ? 'Memory status: illustrative demo data' : 'Memory status: backend API records'}</h2>
        <p className="mt-1 text-[11px] leading-5 text-amber-800">
          {isMockMode
            ? 'All incidents, outcomes, and insights below are synthetic examples for the interface. These are not persistent memories and have not been retrieved from Hindsight.'
            : 'Records are supplied by the configured backend API. The frontend does not connect to Hindsight directly; confirm the backend memory source and retrieval behavior with the agreed API contract.'}
        </p>
      </div>
    </div>
  )
}

export default function MemoryOverview({ stats }: { stats: MemoryOverviewStats }) {
  return (
    <section className="mb-5">
      <div className="mb-3 flex items-center justify-between gap-3">
        <div>
          <h2 className="text-sm font-semibold text-slate-900">Memory overview</h2>
          <p className="mt-1 text-xs text-slate-500">{isMockMode ? 'Illustrative demo statistics only' : 'Statistics returned by the backend'}</p>
        </div>
        <span className="rounded-full bg-slate-100 px-2.5 py-1 text-[9px] font-semibold uppercase tracking-wide text-slate-500">{isMockMode ? 'Demo stats' : 'API stats'}</span>
      </div>
      <div className="grid gap-4 sm:grid-cols-2 xl:grid-cols-4">
        {statsCards.map(({ key, label, icon: Icon, color }) => (
          <article key={key} className="rounded-2xl border border-slate-200/80 bg-white p-5 shadow-sm shadow-slate-200/40">
            <div className="flex items-start justify-between gap-3">
              <div>
                <p className="text-[13px] font-medium text-slate-500">{label}</p>
                <p className="mt-3 text-[30px] font-semibold leading-none tracking-tight text-slate-900">
                  {stats[key].toLocaleString()}
                </p>
              </div>
              <span className={`flex size-10 items-center justify-center rounded-xl ${color}`}><Icon size={19} /></span>
            </div>
            <p className="mt-4 text-[10px] font-semibold uppercase tracking-wide text-slate-400">{isMockMode ? 'Demo statistic' : 'Backend statistic'}</p>
          </article>
        ))}
      </div>
    </section>
  )
}
