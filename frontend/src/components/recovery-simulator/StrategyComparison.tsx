import {
  CartesianGrid,
  ResponsiveContainer,
  Scatter,
  ScatterChart,
  Tooltip,
  XAxis,
  YAxis,
  ZAxis,
} from 'recharts'
import type { RecoveryStrategy, RecoveryStrategyKey, SimulationScenario } from '../../types/simulation'
import { strategyChartColors } from '../../data/simulationMockData'
import { isMockMode } from '../../services/apiConfig'

const riskStyles = {
  Low: 'bg-emerald-50 text-emerald-700 ring-emerald-600/15',
  Medium: 'bg-amber-50 text-amber-700 ring-amber-600/15',
  High: 'bg-orange-50 text-orange-700 ring-orange-600/15',
  Critical: 'bg-rose-50 text-rose-700 ring-rose-600/15',
}

const feasibilityStyles = {
  Feasible: 'bg-emerald-50 text-emerald-700',
  Conditional: 'bg-amber-50 text-amber-700',
  'Not feasible': 'bg-slate-100 text-slate-600',
}

function formatCurrency(value: number): string {
  return new Intl.NumberFormat('en-US', { style: 'currency', currency: 'USD', maximumFractionDigits: 0 }).format(value)
}

function StrategyChartTooltip({
  active,
  payload,
}: {
  active?: boolean
  payload?: Array<{ payload: RecoveryStrategy }>
}) {
  if (!active || !payload?.length) return null
  const strategy = payload[0].payload
  return (
    <div className="rounded-xl border border-slate-200 bg-white p-3 shadow-lg">
      <p className="text-xs font-semibold text-slate-800">{strategy.name}</p>
      <p className="mt-1 text-[11px] text-slate-500">Added cost: {formatCurrency(strategy.additionalCost)}</p>
      <p className="text-[11px] text-slate-500">Delivery delay: {strategy.deliveryDelayDays} days</p>
    </div>
  )
}

export default function StrategyComparison({
  scenario,
  selectedStrategyKey,
  onSelect,
}: {
  scenario: SimulationScenario
  selectedStrategyKey: RecoveryStrategyKey
  onSelect: (key: RecoveryStrategyKey) => void
}) {
  return (
    <div className="mb-5 grid gap-5 xl:grid-cols-3">
      <section className="overflow-hidden rounded-2xl border border-slate-200/80 bg-white shadow-sm shadow-slate-200/40 xl:col-span-2">
        <div className="px-5 pb-4 pt-5 sm:px-6">
          <h2 className="text-sm font-semibold text-slate-900">Strategy comparison</h2>
          <p className="mt-1 text-xs text-slate-500">{isMockMode ? 'Side-by-side illustrative estimates · Not real predictions' : 'Side-by-side estimates returned by the backend'}</p>
        </div>
        <div className="overflow-x-auto">
          <table className="w-full min-w-[760px] text-left">
            <thead>
              <tr className="border-y border-slate-100 bg-slate-50/70 text-[10px] font-semibold uppercase tracking-[0.1em] text-slate-400">
                <th className="px-5 py-3 sm:px-6">Strategy</th><th className="px-4 py-3">Additional cost</th><th className="px-4 py-3">Delivery delay</th><th className="px-4 py-3">Shortage</th><th className="px-4 py-3">Risk</th><th className="px-4 py-3">Feasibility</th>
              </tr>
            </thead>
            <tbody className="divide-y divide-slate-100">
              {scenario.strategies.map((strategy) => (
                <tr key={strategy.key} className={`cursor-pointer text-xs text-slate-600 transition hover:bg-blue-50/50 ${selectedStrategyKey === strategy.key ? 'bg-blue-50/50' : ''}`} onClick={() => onSelect(strategy.key)}>
                  <td className="whitespace-nowrap px-5 py-3.5 font-semibold text-slate-800 sm:px-6">
                    <span className="inline-flex items-center gap-2"><span className="size-2 rounded-full" style={{ backgroundColor: strategyChartColors[strategy.key] }} />{strategy.name}</span>
                  </td>
                  <td className="whitespace-nowrap px-4 py-3.5">{formatCurrency(strategy.additionalCost)}</td>
                  <td className="whitespace-nowrap px-4 py-3.5">{strategy.deliveryDelayDays} days</td>
                   <td className="whitespace-nowrap px-4 py-3.5">{strategy.projectedShortageUnits == null ? 'Unavailable' : `${strategy.projectedShortageUnits.toLocaleString()} units`}</td>
                  <td className="whitespace-nowrap px-4 py-3.5"><span className={`rounded-full px-2 py-1 text-[10px] font-semibold ring-1 ring-inset ${riskStyles[strategy.riskLevel]}`}>{strategy.riskLevel}</span></td>
                  <td className="whitespace-nowrap px-4 py-3.5"><span className={`rounded-full px-2 py-1 text-[10px] font-medium ${feasibilityStyles[strategy.feasibility]}`}>{strategy.feasibility}</span></td>
                </tr>
              ))}
            </tbody>
          </table>
        </div>
      </section>
      <section className="rounded-2xl border border-slate-200/80 bg-white p-5 shadow-sm shadow-slate-200/40 sm:p-6">
        <div className="mb-2">
          <h2 className="text-sm font-semibold text-slate-900">Cost vs delivery time</h2>
          <p className="mt-1 text-xs text-slate-500">{isMockMode ? 'Each point is a demo strategy' : 'Each point is a returned strategy'}</p>
        </div>
        <div className="h-[245px] w-full">
          <ResponsiveContainer width="100%" height="100%">
            <ScatterChart margin={{ top: 12, right: 12, bottom: 12, left: 0 }}>
              <CartesianGrid stroke="#eef2f7" />
              <XAxis type="number" dataKey="deliveryDelayDays" name="Delivery delay" unit=" days" axisLine={false} tickLine={false} tick={{ fill: '#94a3b8', fontSize: 10 }} label={{ value: 'Delivery delay (days)', position: 'insideBottom', offset: -5, fill: '#64748b', fontSize: 10 }} />
              <YAxis type="number" dataKey="additionalCost" name="Additional cost" tickFormatter={(value: number) => `$${Math.round(value / 1000)}k`} axisLine={false} tickLine={false} tick={{ fill: '#94a3b8', fontSize: 10 }} />
              <ZAxis range={[100, 100]} />
              <Tooltip content={<StrategyChartTooltip />} />
              <Scatter
                data={scenario.strategies}
                fill="#2563eb"
                shape={(props) => {
                  const { cx, cy, payload } = props as { cx: number; cy: number; payload: RecoveryStrategy }
                  return <circle cx={cx} cy={cy} r={selectedStrategyKey === payload.key ? 8 : 6} fill={strategyChartColors[payload.key]} stroke={selectedStrategyKey === payload.key ? '#0f172a' : 'white'} strokeWidth={selectedStrategyKey === payload.key ? 2 : 1} />
                }}
              />
            </ScatterChart>
          </ResponsiveContainer>
        </div>
        <div className="mt-1 flex flex-wrap gap-x-3 gap-y-2">
          {scenario.strategies.map((strategy) => <span key={strategy.key} className="inline-flex items-center gap-1.5 text-[10px] text-slate-500"><span className="size-2 rounded-full" style={{ backgroundColor: strategyChartColors[strategy.key] }} />{strategy.name}</span>)}
        </div>
      </section>
    </div>
  )
}
