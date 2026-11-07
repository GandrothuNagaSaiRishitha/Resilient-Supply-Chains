import {
  CloudLightning,
  Package,
  Ship,
  Truck,
} from 'lucide-react'
import type { DashboardOverview, KpiIcon, KpiTone } from '../../types/dashboard'
import { isMockMode } from '../../services/apiConfig'

const icons: Record<KpiIcon, typeof CloudLightning> = {
  disruptions: CloudLightning,
  shipments: Truck,
  orders: Package,
  inventory: Ship,
}

const tones: Record<KpiTone, string> = {
  blue: 'bg-blue-50 text-blue-600',
  amber: 'bg-amber-50 text-amber-600',
  violet: 'bg-violet-50 text-violet-600',
  rose: 'bg-rose-50 text-rose-600',
}

export default function DashboardKpis({ kpis }: Pick<DashboardOverview, 'kpis'>) {
  return (
    <div className="mb-5 grid gap-4 sm:grid-cols-2 xl:grid-cols-4">
      {kpis.map((kpi) => {
        const Icon = icons[kpi.icon]
        return (
          <article
            key={kpi.id}
            className="rounded-2xl border border-slate-200/80 bg-white p-5 shadow-sm shadow-slate-200/40"
          >
            <div className="flex items-start justify-between gap-3">
              <div>
                <p className="text-[13px] font-medium text-slate-500">{kpi.label}</p>
                <p className="mt-3 text-[30px] font-semibold leading-none tracking-tight text-slate-900">
                  {kpi.value}
                  {kpi.unit && (
                    <span className="ml-1.5 text-base font-medium text-slate-500">
                      {kpi.unit}
                    </span>
                  )}
                </p>
              </div>
              <span className={`flex size-10 items-center justify-center rounded-xl ${tones[kpi.tone]}`}>
                <Icon size={19} strokeWidth={1.9} />
              </span>
            </div>
            <p className="mt-4 text-[11px] text-slate-400">{isMockMode ? 'Demo figure' : 'Backend response'}</p>
          </article>
        )
      })}
    </div>
  )
}
