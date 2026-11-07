import { BookOpenCheck, History } from 'lucide-react'
import type { ReplayHistoricalEvidence } from '../types'
import { SectionHeading } from './ReplayPrimitives'
import { isMockMode } from '../../../services/apiConfig'

export default function MemoryEvidence({ evidence }: { evidence: ReplayHistoricalEvidence[] }) {
  return (
    <section className="overflow-hidden rounded-2xl border border-slate-200/80 bg-white shadow-sm shadow-slate-200/40">
      <SectionHeading icon={<History size={17} />} title="Historical evidence considered" subtitle={isMockMode ? 'Synthetic demo records shown for illustration; no Hindsight retrieval occurred.' : 'Historical evidence included in the backend API response. The frontend does not call Hindsight directly.'} />
      {evidence.length === 0 ? (
        <p className="p-6 text-sm text-slate-500">No illustrative evidence is associated with this incident.</p>
      ) : (
        <div className="grid gap-3 p-5 md:grid-cols-2 sm:p-6">
          {evidence.map((item) => (
            <article key={item.id} className="rounded-xl border border-slate-200 bg-white p-4">
              <div className="flex flex-wrap items-center justify-between gap-2">
                <h3 className="text-xs font-semibold text-slate-900">{item.id}</h3>
                <span className="inline-flex items-center gap-1 rounded-full bg-violet-50 px-2 py-1 text-[9px] font-bold text-violet-700"><BookOpenCheck size={11} />{isMockMode ? 'SYNTHETIC EXAMPLE' : 'API EVIDENCE'}</span>
              </div>
              <p className="mt-1 text-[10px] text-slate-400">{item.incidentDate} · {item.crisisType}</p>
              <EvidenceField label="Previous decision" value={item.decision} />
              <EvidenceField label={`Actual outcome${isMockMode ? ' · synthetic' : ''}`} value={item.actualOutcome} />
              <div className="mt-3 rounded-lg bg-blue-50/60 p-3">
                <p className="text-[9px] font-bold uppercase tracking-wide text-blue-700">{isMockMode ? 'Lesson shown in replay' : 'Lesson returned by backend'}</p>
                <p className="mt-1 text-[11px] leading-5 text-slate-600">{item.lesson}</p>
              </div>
            </article>
          ))}
        </div>
      )}
    </section>
  )
}

function EvidenceField({ label, value }: { label: string; value: string }) {
  return <div className="mt-3"><p className="text-[9px] font-bold uppercase tracking-wide text-slate-400">{label}</p><p className="mt-1 text-[11px] leading-5 text-slate-600">{value}</p></div>
}
