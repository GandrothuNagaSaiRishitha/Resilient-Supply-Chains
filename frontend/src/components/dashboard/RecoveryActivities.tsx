import { Activity, Check, Clock3 } from 'lucide-react'
import type { DashboardOverview } from '../../types/dashboard'
import { isMockMode } from '../../services/apiConfig'

export default function RecoveryActivities({
  activities,
}: {
  activities: DashboardOverview['recoveryActivities']
}) {
  return (
    <section className="rounded-2xl border border-slate-200/80 bg-white p-5 shadow-sm shadow-slate-200/40 sm:p-6">
      <div className="mb-5 flex items-center justify-between gap-3">
        <div>
          <h3 className="text-sm font-semibold text-slate-900">Recent recovery activities</h3>
          <p className="mt-1 text-xs text-slate-500">{isMockMode ? 'Response team activity · Demo data' : 'Response team activity'}</p>
        </div>
        <span className="flex size-9 items-center justify-center rounded-xl bg-blue-50 text-blue-600">
          <Activity size={18} />
        </span>
      </div>
      <div className="grid gap-3 md:grid-cols-3">
        {activities.length === 0 ? <p className="rounded-lg bg-slate-50 p-4 text-xs text-slate-500 md:col-span-3">No recovery activities to display.</p> : activities.map((activity) => (
          <article key={activity.id} className="flex gap-3 rounded-xl border border-slate-100 bg-slate-50/70 p-4">
            <span className="mt-0.5 flex size-7 shrink-0 items-center justify-center rounded-full bg-emerald-100 text-emerald-700">
              {activity.status === 'Completed' ? <Check size={14} /> : <Clock3 size={14} />}
            </span>
            <div className="min-w-0">
              <h4 className="text-xs font-semibold leading-5 text-slate-800">{activity.title}</h4>
              <p className="mt-1 text-[11px] leading-5 text-slate-500">{activity.description}</p>
              <p className="mt-3 text-[10px] text-slate-400">{activity.owner} · {activity.time}</p>
            </div>
            <span className="ml-auto hidden shrink-0 items-center self-start text-[10px] font-medium text-emerald-700 sm:flex">
              {activity.status === 'Completed' ? 'Completed' : 'In progress'}
            </span>
          </article>
        ))}
      </div>
    </section>
  )
}
