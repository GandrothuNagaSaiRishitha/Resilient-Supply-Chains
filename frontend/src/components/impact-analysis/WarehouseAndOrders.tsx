import { AlertTriangle, ShieldAlert, Warehouse } from 'lucide-react'
import type { ImpactAnalysis, RiskSeverity } from '../../types/impact'
import { isMockMode } from '../../services/apiConfig'

const severityStyles: Record<RiskSeverity, string> = {
  Low: 'bg-emerald-50 text-emerald-700 ring-emerald-600/15',
  Medium: 'bg-amber-50 text-amber-700 ring-amber-600/15',
  High: 'bg-orange-50 text-orange-700 ring-orange-600/15',
  Critical: 'bg-rose-50 text-rose-700 ring-rose-600/15',
}
const severityOrder: RiskSeverity[] = ['Low', 'Medium', 'High', 'Critical']

function SeverityBadge({ severity }: { severity: RiskSeverity }) {
  return (
    <span className={`inline-flex rounded-full px-2.5 py-1 text-[10px] font-semibold ring-1 ring-inset ${severityStyles[severity]}`}>
      {severity}
    </span>
  )
}

export function WarehouseImpactTable({
  warehouseImpacts,
}: Pick<ImpactAnalysis, 'warehouseImpacts'>) {
  return (
    <section className="overflow-hidden rounded-2xl border border-slate-200/80 bg-white shadow-sm shadow-slate-200/40 xl:col-span-2">
      <div className="flex items-center justify-between gap-3 px-5 pb-4 pt-5 sm:px-6">
        <div>
          <h2 className="text-sm font-semibold text-slate-900">Warehouse inventory impact</h2>
          <p className="mt-1 text-xs text-slate-500">{isMockMode ? 'Illustrative on-hand and exposure by facility' : 'On-hand inventory and exposure by facility'}</p>
        </div>
        <Warehouse size={18} className="text-slate-400" />
      </div>
      {warehouseImpacts.length === 0 ? (
        <div className="p-8 text-center text-sm text-slate-500">No warehouse impact details are available.</div>
      ) : (
        <div className="overflow-x-auto">
          <table className="w-full min-w-[620px] text-left">
            <thead>
              <tr className="border-y border-slate-100 bg-slate-50/70 text-[10px] font-semibold uppercase tracking-[0.1em] text-slate-400">
                <th className="px-5 py-3 sm:px-6">Warehouse</th><th className="px-4 py-3">Available</th><th className="px-4 py-3">At risk</th><th className="px-4 py-3">Coverage</th><th className="px-4 py-3">Risk</th>
              </tr>
            </thead>
            <tbody className="divide-y divide-slate-100">
              {warehouseImpacts.map((warehouse) => (
                <tr key={warehouse.id} className="text-xs text-slate-600">
                  <td className="px-5 py-3.5 sm:px-6">
                    <span className="block font-semibold text-slate-800">{warehouse.warehouse}</span>
                    <span className="mt-0.5 block text-[10px] text-slate-400">{warehouse.location}</span>
                  </td>
                  <td className="whitespace-nowrap px-4 py-3.5">{warehouse.availableInventory.toLocaleString()} units</td>
                  <td className="whitespace-nowrap px-4 py-3.5 font-medium text-rose-700">{warehouse.inventoryAtRisk.toLocaleString()} units</td>
                  <td className="whitespace-nowrap px-4 py-3.5">{warehouse.coverageDays} days</td>
                  <td className="whitespace-nowrap px-4 py-3.5"><SeverityBadge severity={warehouse.severity} /></td>
                </tr>
              ))}
            </tbody>
          </table>
        </div>
      )}
    </section>
  )
}

export function RiskSeverityPanel({
  severityIndicators,
}: Pick<ImpactAnalysis, 'severityIndicators'>) {
  return (
    <section className="rounded-2xl border border-slate-200/80 bg-white p-5 shadow-sm shadow-slate-200/40 sm:p-6">
      <div className="mb-5 flex items-start justify-between">
        <div>
          <h2 className="text-sm font-semibold text-slate-900">Risk severity</h2>
          <p className="mt-1 text-xs text-slate-500">{isMockMode ? 'Modeled exposure indicators · Demo' : 'Exposure indicators'}</p>
        </div>
        <ShieldAlert size={18} className="text-slate-400" />
      </div>
      <div className="space-y-3">
        {severityOrder.map((severity) => {
          const indicator = severityIndicators.find((item) => item.severity === severity)
          return (
            <div key={severity} className="flex items-center gap-3 rounded-xl border border-slate-100 p-3">
              <SeverityBadge severity={severity} />
              <p className="min-w-0 flex-1 truncate text-[11px] text-slate-500">{indicator?.description ?? 'No records at this level'}</p>
              <span className="text-sm font-semibold text-slate-800">{indicator?.count ?? 0}</span>
            </div>
          )
        })}
      </div>
    </section>
  )
}

export function CustomerOrdersTable({
  customerOrders,
}: Pick<ImpactAnalysis, 'customerOrders'>) {
  return (
    <section className="mb-5 overflow-hidden rounded-2xl border border-slate-200/80 bg-white shadow-sm shadow-slate-200/40">
      <div className="flex items-center justify-between gap-3 px-5 pb-4 pt-5 sm:px-6">
        <div>
          <h2 className="text-sm font-semibold text-slate-900">Customer orders at risk</h2>
          <p className="mt-1 text-xs text-slate-500">{isMockMode ? 'Illustrative order exposure and delay estimates' : 'Order exposure and delay estimates'}</p>
        </div>
        <AlertTriangle size={18} className="text-amber-500" />
      </div>
      {customerOrders.length === 0 ? (
        <div className="p-8 text-center text-sm text-slate-500">No customer orders are at risk.</div>
      ) : (
        <div className="overflow-x-auto">
          <table className="w-full min-w-[620px] text-left">
            <thead>
              <tr className="border-y border-slate-100 bg-slate-50/70 text-[10px] font-semibold uppercase tracking-[0.1em] text-slate-400">
                <th className="px-5 py-3 sm:px-6">Order ID</th><th className="px-4 py-3">Customer</th><th className="px-4 py-3">Order value at risk</th><th className="px-4 py-3">Priority</th><th className="px-4 py-3">Expected delay</th>
              </tr>
            </thead>
            <tbody className="divide-y divide-slate-100">
              {customerOrders.map((order) => (
                <tr key={order.id} className="text-xs text-slate-600">
                  <td className="whitespace-nowrap px-5 py-3.5 font-semibold text-slate-800 sm:px-6">{order.id}</td>
                  <td className="whitespace-nowrap px-4 py-3.5">{order.customer}</td>
                  <td className="whitespace-nowrap px-4 py-3.5">{order.orderValue.toLocaleString('en-US', { style: 'currency', currency: 'USD', maximumFractionDigits: 0 })}</td>
                  <td className="whitespace-nowrap px-4 py-3.5"><SeverityBadge severity={order.priority} /></td>
                  <td className="whitespace-nowrap px-4 py-3.5">{order.expectedDelayDays} days</td>
                </tr>
              ))}
            </tbody>
          </table>
        </div>
      )}
    </section>
  )
}
