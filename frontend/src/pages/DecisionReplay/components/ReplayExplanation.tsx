import { Info } from 'lucide-react'
import type { DecisionReplayRecord } from '../types'
import { DemoBadge } from './ReplayPrimitives'
import { isMockMode } from '../../../services/apiConfig'

export default function ReplayExplanation({ record }: { record: DecisionReplayRecord }) {
  return (
    <aside className="rounded-2xl border border-blue-100 bg-blue-50/60 p-5 sm:p-6">
      <div className="flex flex-col justify-between gap-3 sm:flex-row sm:items-start">
        <div className="flex items-start gap-3">
          <span className="flex size-9 shrink-0 items-center justify-center rounded-xl bg-white text-blue-600"><Info size={17} /></span>
          <div>
            <h2 className="text-sm font-semibold text-slate-900">Why the replay recommendation changed</h2>
            <p className="mt-2 text-xs leading-6 text-slate-600">{record.evidenceExplanation}</p>
          </div>
        </div>
        <DemoBadge>{isMockMode ? 'Illustrative demo data' : 'Backend API data'}</DemoBadge>
      </div>
      <p className="mt-4 border-t border-blue-100 pt-3 text-[10px] leading-5 text-slate-500">
        {isMockMode
          ? 'This page presents static, authored comparisons from illustrative demo records. It does not run an AI decision engine, query Hindsight, or represent a real replay of production data.'
          : 'The backend compares the incident baseline with organization-scoped Hindsight evidence. This replay is analytical and does not change the original decision.'}
      </p>
    </aside>
  )
}
