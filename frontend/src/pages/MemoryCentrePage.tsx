import { AlertCircle, CalendarDays, RotateCcw } from 'lucide-react'
import IncidentTimeline from '../components/memory-centre/IncidentTimeline'
import MemoryDetailDialog from '../components/memory-centre/MemoryDetailDialog'
import { LearnedInsights, MemoryLifecycle } from '../components/memory-centre/MemoryInsightsAndLifecycle'
import MemoryOverview, { MemoryStatusNotice } from '../components/memory-centre/MemoryOverview'
import RetrievedMemories from '../components/memory-centre/RetrievedMemories'
import MemorySearchFilters from '../components/memory-centre/MemorySearchFilters'
import { useMemoryCentre } from '../hooks/useMemoryCentre'
import { isMockMode } from '../services/apiConfig'

function LoadingState() {
  return (
    <div className="space-y-5" aria-label="Loading memory centre">
      <div className="h-24 animate-pulse rounded-2xl bg-slate-200/70" />
      <div className="grid gap-4 sm:grid-cols-2 xl:grid-cols-4">
        {Array.from({ length: 4 }, (_, index) => <div key={index} className="h-32 animate-pulse rounded-2xl bg-slate-200/70" />)}
      </div>
      <div className="h-80 animate-pulse rounded-2xl bg-slate-200/70" />
    </div>
  )
}

function ErrorState({ message, onRetry }: { message: string; onRetry: () => void }) {
  return (
    <div className="flex min-h-[320px] flex-col items-center justify-center rounded-2xl border border-rose-200 bg-white p-8 text-center">
      <AlertCircle className="mb-3 text-rose-500" size={28} />
      <h2 className="font-semibold text-slate-900">Memory Centre unavailable</h2>
      <p className="mt-2 max-w-md text-sm leading-6 text-slate-500">{message}</p>
      <button type="button" onClick={onRetry} className="mt-5 inline-flex items-center gap-2 rounded-lg bg-slate-900 px-4 py-2 text-sm font-medium text-white transition hover:bg-slate-700">
        <RotateCcw size={15} />Try again
      </button>
    </div>
  )
}

export default function MemoryCentrePage() {
  const memory = useMemoryCentre()
  if (memory.loading) return <LoadingState />
  if (memory.error && !memory.data) return <ErrorState message={memory.error} onRetry={memory.retry} />
  if (!memory.data) return <ErrorState message={isMockMode ? 'Illustrative memory data could not be loaded. Please try again.' : 'Memory data could not be loaded. Please try again.'} onRetry={memory.retry} />

  return (
    <section className="mx-auto max-w-[1440px]">
      <div className="mb-6 flex flex-col justify-between gap-4 lg:flex-row lg:items-end">
        <div>
          <p className="mb-2 text-sm text-slate-500">Workspace / Memory Centre</p>
          <h1 className="text-2xl font-semibold tracking-tight text-slate-900 sm:text-[28px]">Memory Centre</h1>
          <p className="mt-1.5 text-sm text-slate-500">Explore retained incident outcomes and lessons for supply chain response.</p>
        </div>
        <span className="inline-flex w-fit items-center gap-2 rounded-full border border-amber-200 bg-amber-50 px-3 py-1.5 text-[11px] font-semibold tracking-wide text-amber-800">
        <span className="size-1.5 rounded-full bg-amber-500" />{isMockMode ? 'DEMO RECORDS · NO HINDSIGHT CONNECTION' : 'HINDSIGHT-BACKED MEMORY API'}
        </span>
      </div>

      <MemoryStatusNotice />
      <MemoryOverview stats={memory.data.stats} />
      <MemorySearchFilters
        data={memory.data}
        filters={memory.filters}
        onFilter={memory.setFilter}
        onReset={memory.resetFilters}
      />
      {memory.error && (
        <div role="alert" className="mb-5 flex items-center gap-2 rounded-xl border border-rose-200 bg-rose-50 p-3 text-xs text-rose-800">
          <AlertCircle size={15} />{memory.error}
        </div>
      )}
      <div className="mb-5 grid gap-5 xl:grid-cols-2">
        <IncidentTimeline
          memories={memory.memories}
          searching={memory.searching}
          onOpen={(id) => void memory.openDetail(id)}
        />
        <RetrievedMemories
          memories={memory.retrievedMemories}
          crisisTypes={memory.data.crisisTypes}
          selectedCrisisType={memory.selectedCrisisType}
          searching={memory.searching}
          onCrisisTypeChange={(value) => memory.setFilter('crisisType', value)}
          onOpen={(id) => void memory.openDetail(id)}
        />
      </div>
      <LearnedInsights insights={memory.data.insights} />
      <div className="mb-5"><MemoryLifecycle lifecycle={memory.data.lifecycle} /></div>
      <div className="mb-5 flex items-start gap-3 rounded-2xl border border-slate-200 bg-white p-4">
        <CalendarDays size={17} className="mt-0.5 shrink-0 text-slate-400" />
        <p className="text-[11px] leading-5 text-slate-500">
          {isMockMode ? 'Date filters apply to the incident dates in the illustrative demo records. They do not query an external or persistent memory store.' : 'Date filters are applied to organization-scoped Hindsight results returned by the backend.'}
        </p>
      </div>
      <MemoryDetailDialog
        open={memory.detailOpen}
        memory={memory.detail}
        loading={memory.detailLoading}
        error={memory.detailError}
        onClose={memory.closeDetail}
      />
    </section>
  )
}
