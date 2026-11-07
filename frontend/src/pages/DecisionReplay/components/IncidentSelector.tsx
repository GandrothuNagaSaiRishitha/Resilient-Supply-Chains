import { ChevronDown, History } from 'lucide-react'
import type { SimulationIncident } from '../../../types/simulation'

export default function IncidentSelector({
  incidents,
  value,
  disabled,
  onChange,
}: {
  incidents: SimulationIncident[]
  value: string
  disabled: boolean
  onChange: (id: string) => void
}) {
  return (
    <section className="flex flex-col gap-3 rounded-2xl border border-slate-200/80 bg-white p-4 shadow-sm shadow-slate-200/40 sm:flex-row sm:items-center sm:px-5">
      <div className="flex items-center gap-3">
        <span className="flex size-9 items-center justify-center rounded-xl bg-blue-50 text-blue-600"><History size={18} /></span>
        <div>
          <label htmlFor="replay-incident" className="block text-xs font-semibold text-slate-800">Previous crisis incident</label>
          <p className="mt-0.5 text-[10px] text-slate-400">Choose an illustrative demo record</p>
        </div>
      </div>
      <div className="relative min-w-0 flex-1 sm:max-w-2xl sm:pl-3">
        <select id="replay-incident" value={value} onChange={(event) => onChange(event.target.value)} disabled={disabled || incidents.length === 0} className="w-full appearance-none rounded-lg border border-slate-200 bg-slate-50 py-2.5 pl-3 pr-9 text-sm text-slate-800 outline-none transition focus:border-blue-400 focus:ring-4 focus:ring-blue-500/10 disabled:opacity-60">
          {incidents.length === 0 && <option value="">No demo incidents available</option>}
          {incidents.map((incident) => <option key={incident.id} value={incident.id}>{incident.id} · {incident.crisisType} — {incident.title}</option>)}
        </select>
        <ChevronDown size={16} className="pointer-events-none absolute right-3 top-1/2 -translate-y-1/2 text-slate-400" />
      </div>
      <span className="w-fit rounded-full border border-blue-200 bg-blue-50 px-2.5 py-1 text-[9px] font-bold uppercase tracking-[0.1em] text-blue-700">Demo incident history</span>
    </section>
  )
}
