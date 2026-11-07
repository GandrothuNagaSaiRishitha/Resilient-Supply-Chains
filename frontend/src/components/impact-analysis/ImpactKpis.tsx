import {
  Building2,
  CircleDollarSign,
  ClipboardList,
  PackageOpen,
} from 'lucide-react'
import type { ImpactAnalysis } from '../../types/impact'
import { isMockMode } from '../../services/apiConfig'

const icons = [ClipboardList, PackageOpen, Building2, CircleDollarSign]
const iconStyles = [
  'bg-blue-50 text-blue-600',
  'bg-rose-50 text-rose-600',
  'bg-violet-50 text-violet-600',
  'bg-amber-50 text-amber-600',
]
const severityStyles = {
  Low: 'bg-emerald-50 text-emerald-700 ring-emerald-600/15',
  Medium: 'bg-amber-50 text-amber-700 ring-amber-600/15',
  High: 'bg-orange-50 text-orange-700 ring-orange-600/15',
  Critical: 'bg-rose-50 text-rose-700 ring-rose-600/15',
}

export default function ImpactKpis({ kpis }: Pick<ImpactAnalysis, 'kpis'>) {
  return (
    <div className="mb-5 grid gap-4 sm:grid-cols-2 xl:grid-cols-4">
      {kpis.map((kpi, index) => {
        const Icon = icons[index % icons.length]
        return (
          <article key={kpi.id} className="rounded-2xl border border-slate-200/80 bg-white p-5 shadow-sm shadow-slate-200/40">
            <div className="flex items-start justify-between gap-3">
              <div>
                <p className="text-[13px] font-medium text-slate-500">{kpi.label}</p>
                <p className="mt-3 text-[26px] font-semibold leading-none tracking-tight text-slate-900">{kpi.formattedValue}</p>
              </div>
              <span className={`flex size-10 items-center justify-center rounded-xl ${iconStyles[index % iconStyles.length]}`}>
                <Icon size={19} strokeWidth={1.9} />
              </span>
            </div>
            <div className="mt-4 flex items-center justify-between">
              <span className="text-[11px] text-slate-400">{isMockMode ? 'Illustrative demo' : 'Backend response'}</span>
              <span className={`rounded-full px-2.5 py-1 text-[10px] font-semibold ring-1 ring-inset ${severityStyles[kpi.severity]}`}>
                {kpi.severity}
              </span>
            </div>
          </article>
        )
      })}
    </div>
  )
}
