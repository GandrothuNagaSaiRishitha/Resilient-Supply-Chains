import { Info } from 'lucide-react'
import { isMockMode } from '../../services/apiConfig'

export default function DecisionExplanation({ notice }: { notice?: string }) {
  return (
    <aside className="rounded-2xl border border-slate-200 bg-slate-50/80 p-5 sm:p-6">
      <div className="flex items-start gap-3">
        <span className="flex size-9 shrink-0 items-center justify-center rounded-xl bg-white text-blue-600 shadow-sm"><Info size={17} /></span>
        <div>
          <h2 className="text-xs font-semibold text-slate-800">{isMockMode ? 'How this demo recommendation is assembled' : 'Recommendation data source'}</h2>
          <p className="mt-1 text-xs leading-5 text-slate-600">{notice ?? (isMockMode ? 'Current recommendation and historical examples are illustrative demo data.' : 'Recommendation and evidence details are returned by the configured backend API. Confirm calculation and memory provenance with the backend contract.')}</p>
        </div>
      </div>
      <div className="mt-4 grid gap-3 sm:grid-cols-3">
        <ExplanationStep number="01" title={isMockMode ? 'Scenario estimates' : 'Recommendation service'} text={isMockMode ? 'Strategy costs, delays, shortage estimates, and feasibility come from fixed illustrative simulation records.' : 'Recommendation and scenario results are returned by the configured API. Verify endpoint and estimate semantics with the backend team.'} />
        <ExplanationStep number="02" title={isMockMode ? 'Synthetic examples' : 'Historical evidence'} text={isMockMode ? 'Example incidents and lessons are static demo content; no Hindsight retrieval or live AI analysis occurs.' : 'Evidence is provided by the backend response. This frontend does not connect to Hindsight directly.'} />
        <ExplanationStep number="03" title="Decision & outcome" text={isMockMode ? 'Actions and outcome feedback display demo confirmations and are not persisted to a backend.' : 'Actions and outcome feedback are submitted to the configured backend API.'} />
      </div>
    </aside>
  )
}

function ExplanationStep({ number, title, text }: { number: string; title: string; text: string }) {
  return (
    <div className="rounded-xl border border-slate-200/80 bg-white p-3">
      <span className="text-[9px] font-bold tracking-wider text-blue-600">{number}</span>
      <p className="mt-1 text-[11px] font-semibold text-slate-800">{title}</p>
      <p className="mt-1 text-[10px] leading-5 text-slate-500">{text}</p>
    </div>
  )
}
