import { Clock3, ShieldCheck } from 'lucide-react'
import {
  CartesianGrid,
  Line,
  LineChart,
  ResponsiveContainer,
  Tooltip,
  XAxis,
  YAxis,
} from 'recharts'
import type { DashboardOverview } from '../../types/dashboard'
import { isMockMode } from '../../services/apiConfig'

export default function TrendAndHealth({
  deliveryDelayTrend,
  supplierReliabilitySummary,
}: Pick<DashboardOverview, 'deliveryDelayTrend' | 'supplierReliabilitySummary'>) {
  return (
    <div className="mb-5 grid gap-5 xl:grid-cols-3">
      <section className="rounded-2xl border border-slate-200/80 bg-white p-5 shadow-sm shadow-slate-200/40 sm:p-6 xl:col-span-2">
        <div className="mb-5 flex flex-wrap items-start justify-between gap-4">
          <div>
            <h3 className="text-sm font-semibold text-slate-900">Delivery delay trend</h3>
            <p className="mt-1 text-xs text-slate-500">
              Average delivery delay and delivered orders{isMockMode ? ' · Demo data' : ''}
            </p>
          </div>
          <span className="rounded-lg border border-slate-200 px-2.5 py-1.5 text-[11px] font-medium text-slate-500">
            By month
          </span>
        </div>
        <div className="h-[250px] w-full">
          {deliveryDelayTrend.length === 0 ? (
            <div className="flex h-full items-center justify-center text-xs text-slate-500">
              No delivery trend points are available.
            </div>
          ) : (
            <ResponsiveContainer width="100%" height="100%">
              <LineChart data={deliveryDelayTrend} margin={{ top: 8, right: 8, left: -18, bottom: 0 }}>
                <CartesianGrid stroke="#eef2f7" vertical={false} />
                <XAxis dataKey="month" axisLine={false} tickLine={false} tick={{ fill: '#94a3b8', fontSize: 11 }} dy={10} />
                <YAxis yAxisId="delay" axisLine={false} tickLine={false} tick={{ fill: '#94a3b8', fontSize: 11 }} />
                <YAxis yAxisId="orders" orientation="right" allowDecimals={false} axisLine={false} tickLine={false} tick={{ fill: '#94a3b8', fontSize: 11 }} />
                <Tooltip
                  contentStyle={{ borderRadius: 12, border: '1px solid #e2e8f0', boxShadow: '0 8px 24px rgba(15, 23, 42, 0.08)', fontSize: 12 }}
                  labelStyle={{ color: '#475569', fontWeight: 600 }}
                />
                <Line yAxisId="delay" type="monotone" dataKey="avg_delay_days" name="Average delay (days)" stroke="#2563eb" strokeWidth={2.5} dot={{ r: 3, fill: '#2563eb', strokeWidth: 0 }} activeDot={{ r: 5, strokeWidth: 0 }} />
                <Line yAxisId="orders" type="monotone" dataKey="orders" name="Delivered orders" stroke="#f59e0b" strokeWidth={2.5} dot={{ r: 3, fill: '#f59e0b', strokeWidth: 0 }} activeDot={{ r: 5, strokeWidth: 0 }} />
              </LineChart>
            </ResponsiveContainer>
          )}
        </div>
        <div className="mt-3 flex flex-wrap gap-5 text-xs text-slate-500">
          <span className="inline-flex items-center gap-2"><span className="h-0.5 w-4 rounded bg-blue-600" />Average delay (days)</span>
          <span className="inline-flex items-center gap-2"><span className="h-0.5 w-4 rounded bg-amber-500" />Delivered orders</span>
        </div>
      </section>

      <section className="rounded-2xl border border-slate-200/80 bg-white p-5 shadow-sm shadow-slate-200/40 sm:p-6">
        <div className="flex items-start justify-between">
          <div>
            <h3 className="text-sm font-semibold text-slate-900">Supplier reliability</h3>
            <p className="mt-1 text-xs text-slate-500">{isMockMode ? 'Network metric · Demo' : 'Backend metric'}</p>
          </div>
          <span className="flex size-9 items-center justify-center rounded-xl bg-emerald-50 text-emerald-600">
            <ShieldCheck size={19} />
          </span>
        </div>
        <div className="mt-7 flex items-center gap-3">
          <span className="relative flex size-3">
            <span className="absolute inline-flex size-full animate-ping rounded-full bg-emerald-400 opacity-40" />
            <span className="relative inline-flex size-3 rounded-full bg-emerald-500" />
          </span>
          <span className="text-lg font-semibold text-slate-900">
            {supplierReliabilitySummary.score} / 100
          </span>
        </div>
        <p className="mt-2 text-sm leading-6 text-slate-500">
          Average reliability across {supplierReliabilitySummary.supplierCount} suppliers.
        </p>
        <div className="mt-7">
          <div className="mb-2 flex items-center justify-between text-xs">
            <span className="font-medium text-slate-600">Average reliability score</span>
            <span className="font-semibold text-slate-900">{supplierReliabilitySummary.score}</span>
          </div>
          <div
            className="h-2 overflow-hidden rounded-full bg-slate-100"
            role="progressbar"
            aria-label={`Average supplier reliability score${isMockMode ? ' (demo data)' : ''}`}
            aria-valuenow={supplierReliabilitySummary.score}
            aria-valuemin={0}
            aria-valuemax={100}
          >
            <div className="h-full rounded-full bg-emerald-500 transition-all" style={{ width: `${supplierReliabilitySummary.score}%` }} />
          </div>
        </div>
        <div className="mt-6 flex items-center gap-2 border-t border-slate-100 pt-4 text-[11px] text-slate-400">
          <Clock3 size={13} />
          Updated {supplierReliabilitySummary.generatedAt}
        </div>
      </section>
    </div>
  )
}
