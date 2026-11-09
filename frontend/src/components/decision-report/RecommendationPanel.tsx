import { Check, Lightbulb, ShieldAlert, ListChecks } from 'lucide-react'
import type { DecisionReport } from '../../types/decision'
import { InfoList, StrategyMetrics } from './DecisionUi'
import { strategyForKey } from './decisionUtils'
import { isMockMode } from '../../services/apiConfig'

export default function RecommendationPanel({ report }: { report: DecisionReport }) {
  const recommendation = report.aiRecommendation
  const generated = recommendation?.status === 'generated'
  const strategyKey = generated ? recommendation.strategyKey : report.scenario.recommendedStrategyKey
  const strategy = strategyForKey(report.scenario.strategies, strategyKey)
  return (
    <section className="overflow-hidden rounded-2xl border border-blue-200 bg-white shadow-md shadow-blue-900/5">
      <div className="border-b border-blue-100 bg-gradient-to-r from-blue-50 to-white px-5 py-5 sm:px-7">
        <div className="flex flex-col justify-between gap-3 sm:flex-row sm:items-start">
          <div className="flex items-start gap-3">
            <span className="flex size-11 shrink-0 items-center justify-center rounded-xl bg-blue-600 text-white shadow-sm shadow-blue-600/20"><Lightbulb size={21} /></span>
            <div>
              <p className="text-[10px] font-bold uppercase tracking-[0.14em] text-blue-700">{generated ? 'AI-generated recovery suggestion' : 'Deterministic recovery baseline'}{isMockMode ? ' · demo' : ''}</p>
              <h2 className="mt-1 text-xl font-semibold tracking-tight text-slate-900">{strategy.name}</h2>
            </div>
          </div>
          <span className="w-fit rounded-full border border-blue-200 bg-white px-2.5 py-1 text-[10px] font-semibold text-blue-700">{generated ? 'Groq suggestion' : strategy.feasibility}</span>
        </div>
        <p className="mt-4 max-w-4xl text-sm leading-6 text-slate-600">{recommendation?.rationale ?? report.scenario.recommendationExplanation}</p>
        {recommendation?.notice && <p role="status" className="mt-3 rounded-lg border border-amber-200 bg-amber-50 p-3 text-xs leading-5 text-amber-900">{recommendation.notice}</p>}
        {generated && <p className="mt-2 text-[10px] font-medium text-slate-500">AI-generated suggestion, not a historical record. Historical claims are listed and cited separately below.</p>}
      </div>
      <div className="grid gap-0 lg:grid-cols-[minmax(0,1fr)_minmax(270px,0.75fr)]">
        <div className="grid gap-5 p-5 sm:grid-cols-2 sm:p-6">
          <InfoList title="Estimated impact" icon={<Check size={15} />} items={report.expectedBenefits} color="text-emerald-600" />
          <InfoList title="Risks & trade-offs" icon={<ShieldAlert size={15} />} items={report.risksAndTradeoffs} color="text-amber-600" />
        </div>
        <div className="border-t border-slate-100 bg-slate-50/50 p-5 sm:p-6 lg:border-l lg:border-t-0">
          <h3 className="mb-3 text-xs font-semibold text-slate-800">Estimate & execution checks</h3>
          <StrategyMetrics strategy={strategy} />
          <div className="mt-5">
            <InfoList title="Conditions to verify" icon={<ListChecks size={15} />} items={report.executionConditions} color="text-blue-600" />
          </div>
          <p className="mt-4 border-t border-slate-200 pt-3 text-[10px] leading-4 text-slate-500">
            Evidence strength: <span className="font-semibold capitalize">{recommendation?.evidenceStrength ?? 'not assessed'}</span>
            {report.historicalEvidence.length > 0 ? ` · ${report.historicalEvidence.length} retrieved memories` : ' · no relevant memories returned'}
          </p>
          {!isMockMode && <p className="mt-2 text-[10px] leading-4 text-slate-500">Hindsight reflect: <span className="font-semibold">{report.reflectionStatus === 'used' ? 'synthesis included' : report.reflectionStatus === 'unavailable' ? 'unavailable; recall evidence still used' : report.reflectionStatus === 'empty' ? 'no synthesis returned' : 'not needed without relevant memories'}</span></p>}
        </div>
      </div>
    </section>
  )
}
