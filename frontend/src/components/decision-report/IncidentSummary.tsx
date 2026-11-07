import { AlertCircle, ChevronDown } from 'lucide-react'
import type { DecisionReport } from '../../types/decision'
import type { SimulationIncident } from '../../types/simulation'
import { SectionHeader } from './DecisionUi'
import { inputClassName } from './decisionUtils'
import { isMockMode } from '../../services/apiConfig'

const urgencyStyles = {
  Low: 'bg-emerald-50 text-emerald-700 ring-emerald-600/15',
  Medium: 'bg-amber-50 text-amber-700 ring-amber-600/15',
  High: 'bg-orange-50 text-orange-700 ring-orange-600/15',
  Critical: 'bg-rose-50 text-rose-700 ring-rose-600/15',
}

export function IncidentSelector({
  incidents,
  incidentId,
  loading,
  onChange,
}: {
  incidents: SimulationIncident[]
  incidentId: string
  loading: boolean
  onChange: (id: string) => void
}) {
  const incident = incidents.find(({ id }) => id === incidentId)
  return (
    <div className="mb-5 flex flex-col gap-3 rounded-2xl border border-slate-200/80 bg-white p-4 shadow-sm shadow-slate-200/40 sm:flex-row sm:items-center sm:px-5">
      <div className="flex items-center gap-3">
        <span className="flex size-9 items-center justify-center rounded-xl bg-blue-50 text-blue-600"><AlertCircle size={18} /></span>
        <div>
          <label htmlFor="decision-incident" className="block text-xs font-semibold text-slate-800">Decision for incident</label>
          <p className="mt-0.5 text-[10px] text-slate-400">{isMockMode ? 'Select an illustrative incident' : 'Select an organization incident'}</p>
        </div>
      </div>
      <div className="relative min-w-0 flex-1 sm:max-w-2xl sm:pl-3">
        <select id="decision-incident" value={incidentId} onChange={(event) => onChange(event.target.value)} disabled={loading || incidents.length === 0} className={`${inputClassName} appearance-none bg-slate-50 pr-9 disabled:opacity-60`}>
          {incidents.length === 0 && <option value="">No incidents available</option>}
          {incidents.map((option) => <option key={option.id} value={option.id}>{option.id} · {option.crisisType} — {option.title}</option>)}
        </select>
        <ChevronDown size={16} className="pointer-events-none absolute right-3 top-1/2 -translate-y-1/2 text-slate-400" />
      </div>
      {incident && (
        <div className="flex flex-wrap gap-2 sm:ml-auto sm:justify-end">
          <span className="rounded-full bg-slate-100 px-2.5 py-1 text-[10px] font-semibold text-slate-600">{incident.id}</span>
          <span className="rounded-full bg-blue-50 px-2.5 py-1 text-[10px] font-medium text-blue-700">{incident.crisisType}</span>
        </div>
      )}
    </div>
  )
}

export default function IncidentSummary({ report }: { report: DecisionReport }) {
  return (
    <section className="overflow-hidden rounded-2xl border border-slate-200/80 bg-white shadow-sm shadow-slate-200/40">
      <SectionHeader icon={<AlertCircle size={18} />} title="Incident summary" description="Current incident context and impact." tag={isMockMode ? 'Demo data' : 'Backend data'} />
      <div className="grid gap-5 p-5 sm:p-6 lg:grid-cols-[minmax(0,1.3fr)_minmax(260px,0.7fr)]">
        <div>
          <div className="mb-3 flex flex-wrap items-center gap-2">
            <span className="rounded-full bg-slate-100 px-2.5 py-1 text-[10px] font-semibold text-slate-600">{report.scenario.incident.id}</span>
            <span className="rounded-full bg-blue-50 px-2.5 py-1 text-[10px] font-medium text-blue-700">{report.scenario.incident.crisisType}</span>
            <span className={`rounded-full px-2.5 py-1 text-[10px] font-semibold ring-1 ring-inset ${urgencyStyles[report.incidentContext.urgency]}`}>{report.incidentContext.urgency} urgency</span>
          </div>
          <h2 className="text-base font-semibold text-slate-900">{report.scenario.incident.title}</h2>
          <p className="mt-2 text-sm leading-6 text-slate-600">{report.incidentContext.description}</p>
        </div>
        <div className="rounded-xl border border-slate-100 bg-slate-50/70 p-4">
          <p className="text-[10px] font-bold uppercase tracking-[0.12em] text-slate-400">{isMockMode ? 'Current impact · illustrative' : 'Current impact'}</p>
          <p className="mt-2 text-sm font-semibold leading-6 text-slate-800">{report.incidentContext.currentImpact}</p>
          <p className="mt-2 text-[10px] text-slate-400">Reported {report.scenario.incident.reportedAt}</p>
        </div>
      </div>
    </section>
  )
}
