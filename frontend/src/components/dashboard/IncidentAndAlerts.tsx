import { AlertTriangle } from 'lucide-react'
import type {
  DashboardOverview,
  IncidentSeverity,
  IncidentStatus,
} from '../../types/dashboard'
import { isMockMode } from '../../services/apiConfig'

const severityStyles: Record<IncidentSeverity, string> = {
  Critical: 'bg-rose-50 text-rose-700 ring-rose-600/15',
  High: 'bg-orange-50 text-orange-700 ring-orange-600/15',
  Medium: 'bg-amber-50 text-amber-700 ring-amber-600/15',
  Low: 'bg-slate-100 text-slate-600 ring-slate-500/10',
}

const statusStyles: Record<IncidentStatus, string> = {
  Investigating: 'bg-blue-50 text-blue-700',
  Mitigating: 'bg-amber-50 text-amber-700',
  Monitoring: 'bg-emerald-50 text-emerald-700',
  Resolved: 'bg-slate-100 text-slate-600',
}

export default function IncidentAndAlerts({
  incidents,
  alerts,
}: Pick<DashboardOverview, 'incidents' | 'alerts'>) {
  return (
    <div className="mb-5 grid gap-5 xl:grid-cols-3">
      <section className="overflow-hidden rounded-2xl border border-slate-200/80 bg-white shadow-sm shadow-slate-200/40 xl:col-span-2">
        <div className="flex items-center justify-between gap-3 px-5 pb-4 pt-5 sm:px-6">
          <div>
            <h3 className="text-sm font-semibold text-slate-900">Recent incidents</h3>
            <p className="mt-1 text-xs text-slate-500">{isMockMode ? 'Latest disruption events · Demo data' : 'Latest disruption events'}</p>
          </div>
          <span className="rounded-full bg-slate-100 px-2.5 py-1 text-[10px] font-medium text-slate-500">
            {incidents.length} incidents
          </span>
        </div>
        <div className="overflow-x-auto">
          <table className="w-full min-w-[700px] text-left">
            <thead>
              <tr className="border-y border-slate-100 bg-slate-50/70 text-[10px] font-semibold uppercase tracking-[0.1em] text-slate-400">
                <th className="px-5 py-3 sm:px-6">Incident</th>
                <th className="px-4 py-3">Disruption</th>
                <th className="px-4 py-3">Location</th>
                <th className="px-4 py-3">Severity</th>
                <th className="px-4 py-3">Status</th>
                <th className="px-4 py-3">Date</th>
              </tr>
            </thead>
            <tbody className="divide-y divide-slate-100">
              {incidents.length === 0 ? (
                <tr><td colSpan={6} className="px-5 py-8 text-center text-xs text-slate-500">No incidents to display.</td></tr>
              ) : incidents.map((incident) => (
                <tr key={incident.id} className="text-xs text-slate-600">
                  <td className="whitespace-nowrap px-5 py-3.5 font-semibold text-slate-800 sm:px-6">{incident.id}</td>
                  <td className="whitespace-nowrap px-4 py-3.5">{incident.disruptionType}</td>
                  <td className="whitespace-nowrap px-4 py-3.5">{incident.location}</td>
                  <td className="whitespace-nowrap px-4 py-3.5">
                    <span className={`rounded-full px-2.5 py-1 text-[10px] font-semibold ring-1 ring-inset ${severityStyles[incident.severity]}`}>
                      {incident.severity}
                    </span>
                  </td>
                  <td className="whitespace-nowrap px-4 py-3.5">
                    <span className={`rounded-full px-2.5 py-1 text-[10px] font-medium ${statusStyles[incident.status]}`}>
                      {incident.status}
                    </span>
                  </td>
                  <td className="whitespace-nowrap px-4 py-3.5 text-slate-500">{incident.date}</td>
                </tr>
              ))}
            </tbody>
          </table>
        </div>
      </section>

      <section className="rounded-2xl border border-slate-200/80 bg-white p-5 shadow-sm shadow-slate-200/40 sm:p-6">
        <div className="mb-5">
          <h3 className="text-sm font-semibold text-slate-900">Critical priority alerts</h3>
          <p className="mt-1 text-xs text-slate-500">{isMockMode ? 'Requires attention · Demo data' : 'Requires attention'}</p>
        </div>
        <div className="space-y-4">
          {alerts.length === 0 ? <p className="rounded-lg bg-slate-50 p-4 text-xs text-slate-500">No priority alerts.</p> : alerts.map((alert) => (
            <article key={alert.id} className="flex gap-3 rounded-xl border border-rose-100 bg-rose-50/50 p-3.5">
              <span className="mt-0.5 flex size-8 shrink-0 items-center justify-center rounded-lg bg-rose-100 text-rose-600">
                <AlertTriangle size={16} />
              </span>
              <div className="min-w-0">
                <div className="flex flex-wrap items-center gap-x-2 gap-y-1">
                  <h4 className="text-xs font-semibold text-slate-800">{alert.title}</h4>
                  <span className="rounded-full bg-rose-100 px-1.5 py-0.5 text-[9px] font-bold uppercase tracking-wide text-rose-700">{alert.severity}</span>
                </div>
                <p className="mt-1 text-[11px] leading-5 text-slate-500">{alert.description}</p>
                <p className="mt-2 text-[10px] text-slate-400">{alert.location} · {alert.occurredAt}</p>
              </div>
            </article>
          ))}
        </div>
      </section>
    </div>
  )
}
