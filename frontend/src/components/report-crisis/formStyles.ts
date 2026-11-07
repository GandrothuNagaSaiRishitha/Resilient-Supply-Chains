import type { BusinessUrgency } from '../../types/crisisReport'

export const reportInputClass =
  'w-full rounded-lg border border-slate-200 bg-white px-3 py-2.5 text-sm text-slate-800 outline-none transition placeholder:text-slate-400 focus:border-blue-400 focus:ring-4 focus:ring-blue-500/10'

export const urgencyColors: Record<BusinessUrgency, string> = {
  Low: 'text-slate-600',
  Medium: 'text-amber-700',
  High: 'text-orange-700',
  Critical: 'text-rose-700',
}
