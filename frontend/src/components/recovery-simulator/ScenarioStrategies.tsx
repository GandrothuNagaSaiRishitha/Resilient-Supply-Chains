import { Activity, Clock3, GitCompareArrows, Warehouse, Zap } from 'lucide-react'
import type { FeasibilityStatus, RecoveryStrategy, RecoveryStrategyKey, SimulationScenario } from '../../types/simulation'
import { strategyChartColors } from '../../data/simulationMockData'
import { isMockMode } from '../../services/apiConfig'

const strategyIcons = {
  wait: Clock3,
  reroute: GitCompareArrows,
  'emergency-sourcing': Zap,
  redistribute: Warehouse,
}

const riskStyles = {
  Low: 'bg-emerald-50 text-emerald-700 ring-emerald-600/15',
  Medium: 'bg-amber-50 text-amber-700 ring-amber-600/15',
  High: 'bg-orange-50 text-orange-700 ring-orange-600/15',
  Critical: 'bg-rose-50 text-rose-700 ring-rose-600/15',
}

const feasibilityStyles: Record<FeasibilityStatus, string> = {
  Feasible: 'bg-emerald-50 text-emerald-700',
  Conditional: 'bg-amber-50 text-amber-700',
  'Not feasible': 'bg-slate-100 text-slate-600',
}

function formatCurrency(value: number): string {
  return new Intl.NumberFormat('en-US', { style: 'currency', currency: 'USD', maximumFractionDigits: 0 }).format(value)
}

function StrategyCard({
  strategy,
  isRecommended,
  isSelected,
  onSelect,
}: {
  strategy: RecoveryStrategy
  isRecommended: boolean
  isSelected: boolean
  onSelect: () => void
}) {
  const Icon = strategyIcons[strategy.key]
  return (
    <button type="button" onClick={onSelect} aria-pressed={isSelected} className={`relative flex h-full w-full flex-col rounded-2xl border bg-white p-5 text-left shadow-sm transition hover:-translate-y-0.5 hover:shadow-md ${isSelected ? 'border-blue-500 ring-2 ring-blue-500/15' : 'border-slate-200/80 shadow-slate-200/40'}`}>
      {isRecommended && <span className="absolute right-4 top-4 rounded-full bg-blue-50 px-2.5 py-1 text-[9px] font-bold uppercase tracking-[0.1em] text-blue-700">Recommended</span>}
      <div className="flex items-start gap-3 pr-16">
        <span className="flex size-10 shrink-0 items-center justify-center rounded-xl" style={{ color: strategyChartColors[strategy.key], backgroundColor: `${strategyChartColors[strategy.key]}14` }}><Icon size={19} /></span>
        <div>
          <h3 className="text-sm font-semibold text-slate-900">{strategy.name}</h3>
          <p className="mt-1 text-[11px] leading-5 text-slate-500">{strategy.summary}</p>
        </div>
      </div>
      <div className="mt-5 grid grid-cols-2 gap-3 border-t border-slate-100 pt-4">
        <CardMetric label="Additional cost" value={formatCurrency(strategy.additionalCost)} />
        <CardMetric label="Delivery delay" value={`${strategy.deliveryDelayDays} days`} />
        <CardMetric label="Projected shortage" value={`${strategy.projectedShortageUnits.toLocaleString()} units`} />
        <div>
          <p className="text-[10px] font-medium text-slate-400">Risk level</p>
          <span className={`mt-1 inline-flex rounded-full px-2 py-0.5 text-[10px] font-semibold ring-1 ring-inset ${riskStyles[strategy.riskLevel]}`}>{strategy.riskLevel}</span>
        </div>
      </div>
      <div className="mt-4 flex items-center justify-between gap-2 border-t border-slate-100 pt-3">
        <span className={`rounded-full px-2.5 py-1 text-[10px] font-semibold ${feasibilityStyles[strategy.feasibility]}`}>{strategy.feasibility}</span>
        <span className="text-[10px] text-slate-400">{isSelected ? 'Selected' : 'Select strategy'}</span>
      </div>
    </button>
  )
}

function CardMetric({ label, value }: { label: string; value: string }) {
  return <div><p className="text-[10px] font-medium text-slate-400">{label}</p><p className="mt-1 text-sm font-semibold text-slate-800">{value}</p></div>
}

export default function ScenarioStrategies({
  scenario,
  selectedStrategyKey,
  onSelect,
}: {
  scenario: SimulationScenario
  selectedStrategyKey: RecoveryStrategyKey
  onSelect: (key: RecoveryStrategyKey) => void
}) {
  return (
    <>
      <section className="mb-5 rounded-2xl border border-slate-200/80 bg-white p-5 shadow-sm shadow-slate-200/40 sm:p-6">
        <div className="flex flex-col justify-between gap-5 lg:flex-row">
          <div className="max-w-2xl">
            <div className="mb-2 flex flex-wrap items-center gap-2">
              <span className="rounded-full bg-slate-100 px-2.5 py-1 text-[10px] font-semibold text-slate-600">{scenario.incident.id}</span>
              <span className="rounded-full bg-blue-50 px-2.5 py-1 text-[10px] font-medium text-blue-700">{scenario.incident.crisisType}</span>
            </div>
            <h2 className="text-base font-semibold text-slate-900">{scenario.incident.title}</h2>
            <p className="mt-2 text-xs leading-5 text-slate-500">{scenario.summary}</p>
          </div>
          <div className="grid gap-2 sm:grid-cols-3 lg:min-w-[460px]">
            {scenario.constraints.map((constraint) => (
              <div key={constraint.id} className="rounded-xl border border-slate-100 bg-slate-50/80 p-3">
                <p className="text-[10px] font-medium text-slate-400">{constraint.label}</p>
                <p className="mt-1 text-xs font-semibold leading-5 text-slate-700">{constraint.detail}</p>
              </div>
            ))}
          </div>
        </div>
      </section>
      <div className="mb-5 flex flex-wrap items-end justify-between gap-3">
        <div>
          <h2 className="text-sm font-semibold text-slate-900">Compare recovery strategies</h2>
          <p className="mt-1 text-xs text-slate-500">Compare the modeled trade-offs for this incident.</p>
        </div>
        <span className="inline-flex items-center gap-1.5 rounded-full border border-blue-200 bg-blue-50 px-2.5 py-1 text-[10px] font-semibold text-blue-700"><Activity size={12} />{isMockMode ? 'Illustrative demo simulation' : 'Backend simulation result'}</span>
      </div>
      <div className="mb-5 grid gap-4 md:grid-cols-2 2xl:grid-cols-4">
        {scenario.strategies.map((strategy) => (
          <StrategyCard key={strategy.key} strategy={strategy} isRecommended={strategy.key === scenario.recommendedStrategyKey} isSelected={strategy.key === selectedStrategyKey} onSelect={() => onSelect(strategy.key)} />
        ))}
      </div>
    </>
  )
}
