import { useEffect, useState } from 'react'
import {
  AlertCircle,
  ChartNoAxesCombined,
  ChevronDown,
  PackageOpen,
  RefreshCw,
} from 'lucide-react'
import ImpactAssumptions from '../components/impact-analysis/ImpactAssumptions'
import ImpactKpis from '../components/impact-analysis/ImpactKpis'
import {
  AffectedProductsTable,
  ImpactDistributionChart,
} from '../components/impact-analysis/ProductAndDistribution'
import {
  CustomerOrdersTable,
  RiskSeverityPanel,
  WarehouseImpactTable,
} from '../components/impact-analysis/WarehouseAndOrders'
import { getImpactAnalysis, getImpactIncidents } from '../services/impactService'
import type {
  ImpactAnalysis,
  ImpactIncidentOption,
} from '../types/impact'
import { isMockMode } from '../services/apiConfig'

function LoadingState() {
  return (
    <div className="space-y-5" aria-label="Loading impact analysis">
      <div className="h-24 animate-pulse rounded-2xl bg-slate-200/70" />
      <div className="grid gap-4 sm:grid-cols-2 xl:grid-cols-4">
        {Array.from({ length: 4 }, (_, index) => <div key={index} className="h-32 animate-pulse rounded-2xl bg-slate-200/70" />)}
      </div>
      <div className="grid gap-5 xl:grid-cols-2">
        <div className="h-72 animate-pulse rounded-2xl bg-slate-200/70" />
        <div className="h-72 animate-pulse rounded-2xl bg-slate-200/70" />
      </div>
    </div>
  )
}

function EmptyState() {
  return (
    <div className="flex min-h-[320px] flex-col items-center justify-center rounded-2xl border border-dashed border-slate-300 bg-white p-8 text-center">
      <PackageOpen className="mb-3 text-slate-400" size={30} />
      <h2 className="font-semibold text-slate-900">No demo incidents available</h2>
      <p className="mt-2 max-w-md text-sm leading-6 text-slate-500">There are no illustrative incident records to analyze right now.</p>
    </div>
  )
}

function ErrorState({ onRetry }: { onRetry: () => void }) {
  return (
    <div className="flex min-h-[320px] flex-col items-center justify-center rounded-2xl border border-rose-200 bg-white p-8 text-center">
      <AlertCircle className="mb-3 text-rose-500" size={28} />
      <h2 className="font-semibold text-slate-900">Impact analysis unavailable</h2>
      <p className="mt-2 max-w-md text-sm leading-6 text-slate-500">The illustrative impact data could not be loaded. Please try again.</p>
      <button type="button" onClick={onRetry} className="mt-5 inline-flex items-center gap-2 rounded-lg bg-slate-900 px-4 py-2 text-sm font-medium text-white transition hover:bg-slate-700">
        <RefreshCw size={15} />Try again
      </button>
    </div>
  )
}

function ImpactContent({ analysis }: { analysis: ImpactAnalysis }) {
  return (
    <>
      <ImpactKpis kpis={analysis.kpis} />
      <div className="mb-5 grid gap-5 xl:grid-cols-3">
        <AffectedProductsTable affectedProducts={analysis.affectedProducts} />
        <ImpactDistributionChart distribution={analysis.distribution} />
      </div>
      <div className="mb-5 grid gap-5 xl:grid-cols-3">
        <WarehouseImpactTable warehouseImpacts={analysis.warehouseImpacts} />
        <RiskSeverityPanel severityIndicators={analysis.severityIndicators} />
      </div>
      <CustomerOrdersTable customerOrders={analysis.customerOrders} />
      <ImpactAssumptions assumptions={analysis.assumptions} />
    </>
  )
}

export default function ImpactAnalysisPage() {
  const [incidents, setIncidents] = useState<ImpactIncidentOption[]>([])
  const [selectedIncidentId, setSelectedIncidentId] = useState('')
  const [analysis, setAnalysis] = useState<ImpactAnalysis | null>(null)
  const [loadingIncidents, setLoadingIncidents] = useState(true)
  const [loadingAnalysis, setLoadingAnalysis] = useState(false)
  const [error, setError] = useState(false)
  const [retryKey, setRetryKey] = useState(0)

  useEffect(() => {
    let active = true
    getImpactIncidents()
      .then(({ data }) => {
        if (active) {
          setIncidents(data)
          setLoadingAnalysis(data.length > 0)
          setSelectedIncidentId((current) => current || data[0]?.id || '')
        }
      })
      .catch(() => { if (active) setError(true) })
      .finally(() => { if (active) setLoadingIncidents(false) })
    return () => { active = false }
  }, [retryKey])

  useEffect(() => {
    if (!selectedIncidentId) return
    let active = true
    getImpactAnalysis(selectedIncidentId)
      .then(({ data }) => { if (active) setAnalysis(data) })
      .catch(() => {
        if (active) {
          setAnalysis(null)
          setError(true)
        }
      })
      .finally(() => { if (active) setLoadingAnalysis(false) })
    return () => { active = false }
  }, [selectedIncidentId, retryKey])

  const retry = () => {
    setAnalysis(null)
    setError(false)
    setLoadingIncidents(true)
    setLoadingAnalysis(false)
    setRetryKey((key) => key + 1)
  }
  const selectedIncident = incidents.find(({ id }) => id === selectedIncidentId)

  return (
    <section className="mx-auto max-w-[1440px]">
      <div className="mb-6 flex flex-col justify-between gap-4 lg:flex-row lg:items-end">
        <div>
          <p className="mb-2 text-sm text-slate-500">Workspace / Impact Analysis</p>
          <h1 className="text-2xl font-semibold tracking-tight text-slate-900 sm:text-[28px]">Supply Chain Impact Analysis</h1>
          <p className="mt-1.5 text-sm text-slate-500">Explore the operational and customer impact of a disruption.</p>
        </div>
        <span className="inline-flex w-fit items-center gap-2 rounded-full border border-blue-200 bg-blue-50 px-3 py-1.5 text-[11px] font-semibold tracking-wide text-blue-700">
          <span className="size-1.5 rounded-full bg-blue-500" />{isMockMode ? 'ILLUSTRATIVE DEMO DATA' : 'BACKEND API DATA'}
        </span>
      </div>
      <div className="mb-5 flex flex-col gap-3 rounded-2xl border border-slate-200/80 bg-white p-4 shadow-sm shadow-slate-200/40 sm:flex-row sm:items-center sm:px-5">
        <div className="flex items-center gap-3">
          <span className="flex size-9 items-center justify-center rounded-xl bg-blue-50 text-blue-600"><ChartNoAxesCombined size={18} /></span>
          <div>
            <label htmlFor="impact-incident" className="block text-xs font-semibold text-slate-800">Analyze incident</label>
            <p className="mt-0.5 text-[10px] text-slate-400">Select an illustrative incident</p>
          </div>
        </div>
        <div className="relative min-w-0 flex-1 sm:max-w-xl sm:pl-3">
          <select
            id="impact-incident"
            value={selectedIncidentId}
            onChange={(event) => {
              setSelectedIncidentId(event.target.value)
              setAnalysis(null)
              setLoadingAnalysis(true)
              setError(false)
            }}
            disabled={loadingIncidents || incidents.length === 0}
            className="w-full appearance-none rounded-lg border border-slate-200 bg-slate-50 py-2.5 pl-3 pr-9 text-sm text-slate-800 outline-none transition focus:border-blue-400 focus:ring-4 focus:ring-blue-500/10 disabled:opacity-60"
          >
            {incidents.length === 0 && <option value="">No demo incidents available</option>}
            {incidents.map((incident) => <option key={incident.id} value={incident.id}>{incident.id} · {incident.crisisType} — {incident.title}</option>)}
          </select>
          <ChevronDown size={16} className="pointer-events-none absolute right-3 top-1/2 -translate-y-1/2 text-slate-400" />
        </div>
        {selectedIncident && (
          <div className="flex flex-wrap gap-2 sm:ml-auto sm:justify-end">
            <span className="rounded-full bg-slate-100 px-2.5 py-1 text-[10px] font-semibold text-slate-600">{selectedIncident.id}</span>
            <span className="rounded-full bg-blue-50 px-2.5 py-1 text-[10px] font-medium text-blue-700">{selectedIncident.crisisType}</span>
          </div>
        )}
      </div>
      {loadingIncidents || loadingAnalysis ? <LoadingState /> : error ? <ErrorState onRetry={retry} /> : !analysis ? <EmptyState /> : <ImpactContent analysis={analysis} />}
    </section>
  )
}
