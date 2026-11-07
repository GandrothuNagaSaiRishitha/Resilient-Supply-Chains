import { useEffect, useState } from 'react'
import { RefreshCw, TriangleAlert } from 'lucide-react'
import IncidentAndAlerts from '../components/dashboard/IncidentAndAlerts'
import DashboardKpis from '../components/dashboard/DashboardKpis'
import RecoveryActivities from '../components/dashboard/RecoveryActivities'
import TrendAndHealth from '../components/dashboard/TrendAndHealth'
import { normalizeApiError } from '../services/api'
import { getDashboardOverview } from '../services/dashboardService'
import { isMockMode } from '../services/apiConfig'
import type { DashboardOverview } from '../types/dashboard'

function DashboardLoading() {
  return (
    <div className="space-y-6" aria-label="Loading dashboard">
      <div className="h-20 animate-pulse rounded-2xl bg-slate-200/70" />
      <div className="grid gap-4 sm:grid-cols-2 xl:grid-cols-4">
        {Array.from({ length: 4 }, (_, index) => (
          <div key={index} className="h-32 animate-pulse rounded-2xl bg-slate-200/70" />
        ))}
      </div>
      <div className="grid gap-5 xl:grid-cols-3">
        <div className="h-80 animate-pulse rounded-2xl bg-slate-200/70 xl:col-span-2" />
        <div className="h-80 animate-pulse rounded-2xl bg-slate-200/70" />
      </div>
    </div>
  )
}

function DashboardError({ message, onRetry }: { message: string; onRetry: () => void }) {
  return (
    <div className="flex min-h-[360px] flex-col items-center justify-center rounded-2xl border border-rose-200 bg-white p-8 text-center">
      <TriangleAlert className="mb-3 text-rose-500" size={28} />
      <h2 className="font-semibold text-slate-900">Dashboard unavailable</h2>
      <p className="mt-2 max-w-sm text-sm leading-6 text-slate-500">
        {message}
      </p>
      <button
        type="button"
        onClick={onRetry}
        className="mt-5 inline-flex items-center gap-2 rounded-lg bg-slate-900 px-4 py-2 text-sm font-medium text-white transition hover:bg-slate-700"
      >
        <RefreshCw size={15} />
        Try again
      </button>
    </div>
  )
}

function DashboardContent({ dashboard }: { dashboard: DashboardOverview }) {
  return (
    <>
      <div className="mb-6 flex flex-col justify-between gap-4 sm:flex-row sm:items-end">
        <div>
          <p className="mb-2 text-sm text-slate-500">Workspace / Overview</p>
          <h2 className="text-2xl font-semibold tracking-tight text-slate-900 sm:text-[28px]">
            Supply Chain Overview
          </h2>
          <p className="mt-1.5 text-sm text-slate-500">
            Monitor disruptions and coordinate your response.
          </p>
        </div>
        <span className="inline-flex w-fit items-center gap-2 rounded-full border border-blue-200 bg-blue-50 px-3 py-1.5 text-[11px] font-semibold tracking-wide text-blue-700">
          <span className="size-1.5 rounded-full bg-blue-500" />
          {isMockMode ? 'DEMO DATA · ILLUSTRATIVE VALUES' : 'BACKEND API DATA'}
        </span>
      </div>
      <DashboardKpis kpis={dashboard.kpis} />
      <TrendAndHealth
        deliveryDelayTrend={dashboard.deliveryDelayTrend}
        supplierReliabilitySummary={dashboard.supplierReliabilitySummary}
      />
      <IncidentAndAlerts
        upcomingDeliveries={dashboard.upcomingDeliveries}
        pendingAlerts={dashboard.pendingAlerts}
      />
      <RecoveryActivities suppliers={dashboard.supplierReliability} />
    </>
  )
}

export default function DashboardPage() {
  const [dashboard, setDashboard] = useState<DashboardOverview | null>(null)
  const [loading, setLoading] = useState(true)
  const [error, setError] = useState<string | null>(null)
  const [reloadKey, setReloadKey] = useState(0)

  useEffect(() => {
    let active = true
    getDashboardOverview()
      .then((response) => {
        if (active) setDashboard(response)
      })
      .catch((requestError: unknown) => {
        if (active) setError(normalizeApiError(requestError).message)
      })
      .finally(() => {
        if (active) setLoading(false)
      })

    return () => {
      active = false
    }
  }, [reloadKey])

  const retry = () => {
    setLoading(true)
    setError(null)
    setReloadKey((key) => key + 1)
  }

  if (loading) return <DashboardLoading />
  if (error || !dashboard) {
    return (
      <DashboardError
        message={error ?? 'Dashboard data could not be loaded. Please try again.'}
        onRetry={retry}
      />
    )
  }
  return <DashboardContent dashboard={dashboard} />
}
