import { History } from 'lucide-react'
import type { HistoricalEvidence as HistoricalEvidenceRecord } from '../../types/decision'
import { SectionHeader } from './DecisionUi'
import { isMockMode } from '../../services/apiConfig'

export default function HistoricalEvidence({
  records,
  memoryStatus,
}: {
  records: HistoricalEvidenceRecord[]
  memoryStatus?: 'available' | 'empty' | 'unavailable'
}) {
  return (
    <section className="overflow-hidden rounded-2xl border border-slate-200/80 bg-white shadow-sm shadow-slate-200/40">
      <SectionHeader icon={<History size={18} />} title="Historical evidence" description={isMockMode ? 'Synthetic examples shown for context; they are not actual historical system records.' : 'Historical evidence supplied by the backend response.'} tag={isMockMode ? 'Synthetic demo records' : 'Backend evidence'} />
      {records.length === 0 ? (
        <p role="status" className="p-6 text-center text-sm text-slate-500">
          {memoryStatus === 'unavailable'
            ? 'Hindsight could not be reached. The recommendation uses current incident data and the deterministic baseline only.'
            : 'No relevant historical memories were found for this incident.'}
        </p>
      ) : (
        <div className="grid gap-4 p-5 md:grid-cols-2 sm:p-6">
          {records.map((evidence) => <EvidenceCard key={evidence.id} evidence={evidence} />)}
        </div>
      )}
    </section>
  )
}

function EvidenceCard({ evidence }: { evidence: HistoricalEvidenceRecord }) {
  return (
    <article className="rounded-xl border border-slate-200/80 bg-white p-4">
      <div className="mb-3 flex flex-wrap items-center justify-between gap-2">
        <span className="text-xs font-semibold text-slate-800">{evidence.id}</span>
        <span className="inline-flex items-center gap-1 rounded-full bg-violet-50 px-2 py-1 text-[9px] font-semibold text-violet-700">
        <History size={11} />{isMockMode ? 'SYNTHETIC DEMO' : evidence.verified ? 'VERIFIED RETAINED FACT' : 'RETRIEVED MEMORY'}
        </span>
      </div>
      <p className="text-[11px] text-slate-400">{evidence.incidentDate} · {evidence.crisisType}</p>
      <EvidenceField title="Previous strategy" value={evidence.previousStrategy} />
      <EvidenceField title="Outcome" value={evidence.outcome} />
      <div className="mt-3 rounded-lg bg-slate-50 p-3">
        <p className="text-[10px] font-semibold uppercase tracking-wide text-slate-400">Lesson learned</p>
        <p className="mt-1 text-xs leading-5 text-slate-600">{evidence.lessonLearned}</p>
      </div>
    </article>
  )
}

function EvidenceField({ title, value }: { title: string; value: string }) {
  return (
    <div className="mt-3">
      <p className="text-[10px] font-semibold uppercase tracking-wide text-slate-400">{title}</p>
      <p className="mt-1 text-xs leading-5 text-slate-600">{value}</p>
    </div>
  )
}
