import { AlertTriangle } from 'lucide-react'
import type { DashboardOverview } from '../../types/dashboard'
import { isMockMode } from '../../services/apiConfig'

export default function IncidentAndAlerts({
  upcomingDeliveries,
  pendingAlerts,
}: Pick<DashboardOverview, 'upcomingDeliveries' | 'pendingAlerts'>) {
  return (
    <div className="mb-5 grid gap-5 xl:grid-cols-3">
      <section className="overflow-hidden rounded-2xl border border-slate-200/80 bg-white shadow-sm shadow-slate-200/40 xl:col-span-2">
        <div className="flex items-center justify-between gap-3 px-5 pb-4 pt-5 sm:px-6">
          <div>
            <h3 className="text-sm font-semibold text-slate-900">Upcoming deliveries</h3>
            <p className="mt-1 text-xs text-slate-500">
              Promised within 14 days{isMockMode ? ' · Demo data' : ''}
            </p>
          </div>
          <span className="rounded-full bg-slate-100 px-2.5 py-1 text-[10px] font-medium text-slate-500">
            {upcomingDeliveries.length} deliveries
          </span>
        </div>
        <div className="overflow-x-auto">
          <table className="w-full min-w-[700px] text-left">
            <thead>
              <tr className="border-y border-slate-100 bg-slate-50/70 text-[10px] font-semibold uppercase tracking-[0.1em] text-slate-400">
                <th className="px-5 py-3 sm:px-6">Order</th>
                <th className="px-4 py-3">Supplier</th>
                <th className="px-4 py-3">Promised date</th>
                <th className="px-4 py-3">Priority</th>
                <th className="px-4 py-3">Status</th>
              </tr>
            </thead>
            <tbody className="divide-y divide-slate-100">
              {upcomingDeliveries.length === 0 ? (
                <tr><td colSpan={5} className="px-5 py-8 text-center text-xs text-slate-500">No upcoming deliveries.</td></tr>
              ) : upcomingDeliveries.map((delivery) => (
                <tr key={delivery.id} className="text-xs text-slate-600">
                  <td className="whitespace-nowrap px-5 py-3.5 font-semibold text-slate-800 sm:px-6">{delivery.order_number}</td>
                  <td className="whitespace-nowrap px-4 py-3.5">{delivery.supplier}</td>
                  <td className="whitespace-nowrap px-4 py-3.5 text-slate-500">
                    {new Date(delivery.promised_date).toLocaleDateString()}
                  </td>
                  <td className="whitespace-nowrap px-4 py-3.5 capitalize">{delivery.priority}</td>
                  <td className="whitespace-nowrap px-4 py-3.5 capitalize">{delivery.status.replaceAll('_', ' ')}</td>
                </tr>
              ))}
            </tbody>
          </table>
        </div>
      </section>

      <section className="rounded-2xl border border-slate-200/80 bg-white p-5 shadow-sm shadow-slate-200/40 sm:p-6">
        <div className="mb-5">
          <h3 className="text-sm font-semibold text-slate-900">Pending alerts</h3>
          <p className="mt-1 text-xs text-slate-500">{isMockMode ? 'Requires attention · Demo data' : 'Backend count'}</p>
        </div>
        <div className="flex items-center gap-3 rounded-xl border border-rose-100 bg-rose-50/50 p-4">
          <span className="flex size-8 shrink-0 items-center justify-center rounded-lg bg-rose-100 text-rose-600">
            <AlertTriangle size={16} />
          </span>
          <p className="text-sm text-slate-700">
            <span className="font-semibold">{pendingAlerts}</span>{' '}
            {pendingAlerts === 1 ? 'alert is' : 'alerts are'} pending.
          </p>
        </div>
      </section>
    </div>
  )
}
