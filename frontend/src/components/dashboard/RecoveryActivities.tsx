import { Activity } from 'lucide-react'
import type { DashboardOverview } from '../../types/dashboard'
import { isMockMode } from '../../services/apiConfig'

export default function RecoveryActivities({
  suppliers,
}: {
  suppliers: DashboardOverview['supplierReliability']
}) {
  return (
    <section className="rounded-2xl border border-slate-200/80 bg-white p-5 shadow-sm shadow-slate-200/40 sm:p-6">
      <div className="mb-5 flex items-center justify-between gap-3">
        <div>
          <h3 className="text-sm font-semibold text-slate-900">Supplier reliability details</h3>
          <p className="mt-1 text-xs text-slate-500">
            Reliability and order metrics{isMockMode ? ' · Demo data' : ''}
          </p>
        </div>
        <span className="flex size-9 items-center justify-center rounded-xl bg-blue-50 text-blue-600">
          <Activity size={18} />
        </span>
      </div>
      <div className="grid gap-3 md:grid-cols-3">
        {suppliers.length === 0 ? (
          <p className="rounded-lg bg-slate-50 p-4 text-xs text-slate-500 md:col-span-3">
            No supplier metrics are available.
          </p>
        ) : suppliers.map((supplier) => (
          <article key={supplier.id} className="flex gap-3 rounded-xl border border-slate-100 bg-slate-50/70 p-4">
            <span className="mt-0.5 flex size-7 shrink-0 items-center justify-center rounded-full bg-emerald-100 text-emerald-700">
              <Activity size={14} />
            </span>
            <div className="min-w-0">
              <h4 className="text-xs font-semibold leading-5 text-slate-800">{supplier.name}</h4>
              <p className="mt-1 text-[11px] leading-5 text-slate-500">
                Reliability {supplier.reliability_score} · On-time {Math.round(supplier.on_time_rate * 100)}%
              </p>
              <p className="mt-3 text-[10px] text-slate-400">
                {supplier.delivered_orders} delivered · {supplier.open_orders} open · {supplier.quality_complaints} quality complaints
              </p>
            </div>
          </article>
        ))}
      </div>
    </section>
  )
}
