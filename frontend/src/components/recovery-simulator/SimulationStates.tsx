import { AlertCircle, PackageOpen, RefreshCw } from 'lucide-react'

export function LoadingState() {
  return (
    <div className="space-y-5" aria-label="Loading recovery simulations">
      <div className="h-32 animate-pulse rounded-2xl bg-slate-200/70" />
      <div className="grid gap-4 sm:grid-cols-2 xl:grid-cols-4">
        {Array.from({ length: 4 }, (_, index) => <div key={index} className="h-56 animate-pulse rounded-2xl bg-slate-200/70" />)}
      </div>
      <div className="h-72 animate-pulse rounded-2xl bg-slate-200/70" />
    </div>
  )
}

export function EmptyState() {
  return (
    <div className="flex min-h-[320px] flex-col items-center justify-center rounded-2xl border border-dashed border-slate-300 bg-white p-8 text-center">
      <PackageOpen className="mb-3 text-slate-400" size={30} />
      <h2 className="font-semibold text-slate-900">No incidents available</h2>
      <p className="mt-2 max-w-md text-sm leading-6 text-slate-500">There are no incident scenarios to compare right now.</p>
    </div>
  )
}

export function ErrorState({ onRetry }: { onRetry: () => void }) {
  return (
    <div className="flex min-h-[320px] flex-col items-center justify-center rounded-2xl border border-rose-200 bg-white p-8 text-center">
      <AlertCircle className="mb-3 text-rose-500" size={28} />
      <h2 className="font-semibold text-slate-900">Simulation unavailable</h2>
      <p className="mt-2 max-w-md text-sm leading-6 text-slate-500">Scenario data could not be loaded. Please try again.</p>
      <button type="button" onClick={onRetry} className="mt-5 inline-flex items-center gap-2 rounded-lg bg-slate-900 px-4 py-2 text-sm font-medium text-white transition hover:bg-slate-700">
        <RefreshCw size={15} />Try again
      </button>
    </div>
  )
}
