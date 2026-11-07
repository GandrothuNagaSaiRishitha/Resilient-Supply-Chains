import { ArrowDownRight, ArrowRight, GitCompareArrows } from 'lucide-react'
import type { DecisionReport } from '../../types/decision'
import { ComparisonColumn } from './MemoryComparisonColumn'
import { SectionHeader } from './DecisionUi'
import { strategyForKey } from './decisionUtils'
import { isMockMode } from '../../services/apiConfig'

export default function MemoryComparison({ report }: { report: DecisionReport }) {
  const evidence = report.historicalEvidence.filter((item) =>
    report.memoryComparison.evidenceIds.includes(item.id),
  )
  return (
    <section className="overflow-hidden rounded-2xl border border-slate-200/80 bg-white shadow-sm shadow-slate-200/40">
      <SectionHeader icon={<GitCompareArrows size={18} />} title="Memory-free vs memory-informed comparison" description={isMockMode ? 'A fixed illustrative comparison only—not actual AI reasoning or Hindsight retrieval.' : 'Comparison supplied by the backend; confirm the evidence source and method with the backend contract.'} tag={isMockMode ? 'Illustrative comparison' : 'Backend comparison'} />
      <div className="grid gap-4 p-5 lg:grid-cols-[1fr_auto_1fr] lg:items-stretch sm:p-6">
        <ComparisonColumn
          title={isMockMode ? 'Without historical examples' : 'Memory-free'}
          strategy={strategyForKey(report.scenario.strategies, report.memoryComparison.memoryFreeStrategyKey)}
          explanation={report.memoryComparison.memoryFreeExplanation}
          badge={isMockMode ? 'Baseline demo' : 'Backend result'}
        />
        <div className="flex items-center justify-center text-blue-400">
          <ArrowRight size={20} className="hidden lg:block" />
          <ArrowDownRight size={20} className="lg:hidden" />
        </div>
        <ComparisonColumn
          title={isMockMode ? 'Considering synthetic examples' : 'Memory-informed'}
          strategy={strategyForKey(report.scenario.strategies, report.memoryComparison.memoryInformedStrategyKey)}
          explanation={report.memoryComparison.memoryInformedExplanation}
          badge={isMockMode ? 'Demo only' : 'Backend result'}
        />
      </div>
      <div className="mx-5 mb-5 rounded-xl border border-violet-100 bg-violet-50/60 p-4 sm:mx-6 sm:mb-6">
        <p className="text-[10px] font-bold uppercase tracking-[0.12em] text-violet-700">{isMockMode ? 'Illustrative evidence used' : 'Evidence used'}</p>
        <div className="mt-2 flex flex-wrap gap-2">
          {evidence.map((item) => (
            <span key={item.id} className="rounded-full border border-violet-100 bg-white px-2.5 py-1 text-[10px] font-medium text-violet-800">{item.id} · {item.previousStrategy}</span>
          ))}
        </div>
        <p className="mt-3 text-xs leading-5 text-slate-600">{report.memoryComparison.whatChanged}</p>
      </div>
    </section>
  )
}
