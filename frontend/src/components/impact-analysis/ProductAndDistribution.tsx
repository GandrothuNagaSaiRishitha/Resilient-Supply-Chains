import { Boxes, ChartNoAxesCombined } from 'lucide-react'
import {
  Cell,
  Pie,
  PieChart,
  ResponsiveContainer,
  Tooltip,
} from 'recharts'
import type { ImpactAnalysis } from '../../types/impact'
import { isMockMode } from '../../services/apiConfig'

const colors = ['#2563eb', '#f59e0b', '#8b5cf6', '#14b8a6']
const severityStyles = {
  Low: 'bg-emerald-50 text-emerald-700 ring-emerald-600/15',
  Medium: 'bg-amber-50 text-amber-700 ring-amber-600/15',
  High: 'bg-orange-50 text-orange-700 ring-orange-600/15',
  Critical: 'bg-rose-50 text-rose-700 ring-rose-600/15',
}

export function AffectedProductsTable({
  affectedProducts: products,
}: Pick<ImpactAnalysis, 'affectedProducts'>) {
  return (
    <section className="overflow-hidden rounded-2xl border border-slate-200/80 bg-white shadow-sm shadow-slate-200/40 xl:col-span-2">
      <div className="flex items-center justify-between gap-3 px-5 pb-4 pt-5 sm:px-6">
        <div>
          <h2 className="text-sm font-semibold text-slate-900">Affected products & components</h2>
          <p className="mt-1 text-xs text-slate-500">{isMockMode ? 'Illustrative shortage estimates' : 'Reported shortage estimates'}</p>
        </div>
        <Boxes size={18} className="text-slate-400" />
      </div>
      {products.length === 0 ? (
        <div className="p-8 text-center text-sm text-slate-500">No affected products for this incident.</div>
      ) : (
        <div className="overflow-x-auto">
          <table className="w-full min-w-[640px] text-left">
            <thead>
              <tr className="border-y border-slate-100 bg-slate-50/70 text-[10px] font-semibold uppercase tracking-[0.1em] text-slate-400">
                <th className="px-5 py-3 sm:px-6">Product</th><th className="px-4 py-3">Component</th><th className="px-4 py-3">Supplier</th><th className="px-4 py-3">Shortage</th><th className="px-4 py-3">Risk</th>
              </tr>
            </thead>
            <tbody className="divide-y divide-slate-100">
              {products.map((item) => (
                <tr key={item.id} className="text-xs text-slate-600">
                  <td className="px-5 py-3.5 font-semibold text-slate-800 sm:px-6">{item.product}</td>
                  <td className="whitespace-nowrap px-4 py-3.5">{item.component}</td>
                  <td className="whitespace-nowrap px-4 py-3.5">{item.supplier}</td>
                  <td className="whitespace-nowrap px-4 py-3.5 font-medium text-slate-700">{item.shortage.toLocaleString()} units</td>
                  <td className="whitespace-nowrap px-4 py-3.5"><span className={`rounded-full px-2.5 py-1 text-[10px] font-semibold ring-1 ring-inset ${severityStyles[item.severity]}`}>{item.severity}</span></td>
                </tr>
              ))}
            </tbody>
          </table>
        </div>
      )}
    </section>
  )
}

export function ImpactDistributionChart({
  distribution,
}: Pick<ImpactAnalysis, 'distribution'>) {
  return (
    <section className="rounded-2xl border border-slate-200/80 bg-white p-5 shadow-sm shadow-slate-200/40 sm:p-6">
      <div className="mb-3 flex items-start justify-between">
        <div>
          <h2 className="text-sm font-semibold text-slate-900">Impact distribution</h2>
          <p className="mt-1 text-xs text-slate-500">{isMockMode ? 'Modeled impact share · Demo' : 'Impact distribution'}</p>
        </div>
        <ChartNoAxesCombined size={18} className="text-slate-400" />
      </div>
      {distribution.length === 0 ? (
        <div className="flex h-[210px] items-center justify-center text-sm text-slate-500">No distribution data.</div>
      ) : (
        <>
          <div className="h-[210px] w-full">
            <ResponsiveContainer width="100%" height="100%">
              <PieChart>
                <Pie data={distribution} dataKey="value" nameKey="category" innerRadius={56} outerRadius={82} paddingAngle={3} stroke="none">
                  {distribution.map((item, index) => <Cell key={item.category} fill={colors[index % colors.length]} />)}
                </Pie>
                <Tooltip formatter={(value) => [`${value}%`, 'Impact share']} contentStyle={{ borderRadius: 12, border: '1px solid #e2e8f0', fontSize: 12 }} />
              </PieChart>
            </ResponsiveContainer>
          </div>
          <div className="grid grid-cols-2 gap-x-3 gap-y-2">
            {distribution.map((item, index) => (
              <div key={item.category} className="flex items-center gap-2 text-[11px] text-slate-500">
                <span className="size-2 rounded-full" style={{ backgroundColor: colors[index % colors.length] }} />
                <span className="truncate">{item.category}</span>
                <span className="ml-auto font-semibold text-slate-700">{item.value}%</span>
              </div>
            ))}
          </div>
        </>
      )}
    </section>
  )
}
