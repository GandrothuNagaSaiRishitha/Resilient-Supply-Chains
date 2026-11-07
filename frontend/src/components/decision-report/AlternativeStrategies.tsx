import { ArrowDownRight, BadgeCheck } from 'lucide-react'
import type { DecisionReport, AlternativeStrategyContext } from '../../types/decision'
import type { RecoveryStrategyKey } from '../../types/simulation'
import { SectionHeader } from './DecisionUi'
import { formatCurrency, strategyForKey } from './decisionUtils'
import { isMockMode } from '../../services/apiConfig'

export default function AlternativeStrategies({
  report,
  selectedKey,
  onSelect,
}: {
  report: DecisionReport
  selectedKey: RecoveryStrategyKey | null
  onSelect: (key: RecoveryStrategyKey) => void
}) {
  return (
    <section className="overflow-hidden rounded-2xl border border-slate-200/80 bg-white shadow-sm shadow-slate-200/40">
      <SectionHeader icon={<ArrowDownRight size={18} />} title="Alternative strategies" description="Select an alternative to record a different choice and review its modeled trade-offs." tag={isMockMode ? 'Illustrative estimates' : 'API estimates'} />
      <div className="grid gap-3 p-5 sm:grid-cols-2 sm:p-6 xl:grid-cols-3">
        {report.alternatives.map((alternative) => (
          <AlternativeCard
            key={alternative.strategyKey}
            alternative={alternative}
            report={report}
            selected={selectedKey === alternative.strategyKey && selectedKey !== report.scenario.recommendedStrategyKey}
            onSelect={onSelect}
          />
        ))}
      </div>
    </section>
  )
}

function AlternativeCard({
  alternative,
  report,
  selected,
  onSelect,
}: {
  alternative: AlternativeStrategyContext
  report: DecisionReport
  selected: boolean
  onSelect: (key: RecoveryStrategyKey) => void
}) {
  const strategy = strategyForKey(report.scenario.strategies, alternative.strategyKey)
  return (
    <button
      type="button"
      aria-pressed={selected}
      onClick={() => onSelect(strategy.key)}
      className={`rounded-xl border p-4 text-left transition ${selected ? 'border-blue-400 bg-blue-50/60 ring-2 ring-blue-500/10' : 'border-slate-200 hover:border-blue-200 hover:bg-slate-50'}`}
    >
      <div className="flex items-start justify-between gap-3">
        <div>
          <h3 className="text-xs font-semibold text-slate-900">{strategy.name}</h3>
          <p className="mt-1 text-[10px] leading-5 text-slate-500">{alternative.whyLessSuitable}</p>
        </div>
        {selected && <BadgeCheck size={17} className="shrink-0 text-blue-600" />}
      </div>
      <div className="mt-3 flex flex-wrap gap-x-4 gap-y-1 border-t border-slate-100 pt-3 text-[10px] text-slate-500">
        <span>{formatCurrency(strategy.additionalCost)} additional</span>
        <span>{strategy.deliveryDelayDays} day delay</span>
        <span>{strategy.projectedShortageUnits.toLocaleString()} units short</span>
      </div>
    </button>
  )
}
