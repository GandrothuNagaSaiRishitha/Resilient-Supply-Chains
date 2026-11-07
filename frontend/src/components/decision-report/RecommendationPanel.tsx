import { Check, Lightbulb, ShieldAlert, ListChecks } from 'lucide-react'
import type { DecisionReport } from '../../types/decision'
import { InfoList, StrategyMetrics } from './DecisionUi'
import { strategyForKey } from './decisionUtils'
import { isMockMode } from '../../services/apiConfig'

export default function RecommendationPanel({ report }: { report: DecisionReport }) {
  const strategy = strategyForKey(report.scenario.strategies, report.scenario.recommendedStrategyKey)
  return (
    <section className="overflow-hidden rounded-2xl border border-blue-200 bg-white shadow-md shadow-blue-900/5">
      <div className="border-b border-blue-100 bg-gradient-to-r from-blue-50 to-white px-5 py-5 sm:px-7">
        <div className="flex flex-col justify-between gap-3 sm:flex-row sm:items-start">
          <div className="flex items-start gap-3">
            <span className="flex size-11 shrink-0 items-center justify-center rounded-xl bg-blue-600 text-white shadow-sm shadow-blue-600/20"><Lightbulb size={21} /></span>
            <div>
              <p className="text-[10px] font-bold uppercase tracking-[0.14em] text-blue-700">Recommended recovery strategy{isMockMode ? ' · demo' : ''}</p>
              <h2 className="mt-1 text-xl font-semibold tracking-tight text-slate-900">{strategy.name}</h2>
            </div>
          </div>
          <span className="w-fit rounded-full border border-blue-200 bg-white px-2.5 py-1 text-[10px] font-semibold text-blue-700">{strategy.feasibility}</span>
        </div>
        <p className="mt-4 max-w-4xl text-sm leading-6 text-slate-600">{report.scenario.recommendationExplanation}</p>
      </div>
      <div className="grid gap-0 lg:grid-cols-[minmax(0,1fr)_minmax(270px,0.75fr)]">
        <div className="grid gap-5 p-5 sm:grid-cols-2 sm:p-6">
          <InfoList title="Expected benefits" icon={<Check size={15} />} items={report.expectedBenefits} color="text-emerald-600" />
          <InfoList title="Risks & trade-offs" icon={<ShieldAlert size={15} />} items={report.risksAndTradeoffs} color="text-amber-600" />
        </div>
        <div className="border-t border-slate-100 bg-slate-50/50 p-5 sm:p-6 lg:border-l lg:border-t-0">
          <h3 className="mb-3 text-xs font-semibold text-slate-800">Estimate & execution checks</h3>
          <StrategyMetrics strategy={strategy} />
          <div className="mt-5">
            <InfoList title="Conditions to verify" icon={<ListChecks size={15} />} items={report.executionConditions} color="text-blue-600" />
          </div>
        </div>
      </div>
    </section>
  )
}
