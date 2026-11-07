import type { RecoveryStrategy, RecoveryStrategyKey } from '../../types/simulation'

export const inputClassName =
  'w-full rounded-lg border border-slate-200 bg-white px-3 py-2.5 text-sm text-slate-800 outline-none transition placeholder:text-slate-400 focus:border-blue-400 focus:ring-4 focus:ring-blue-500/10'

export function formatCurrency(value: number): string {
  return new Intl.NumberFormat('en-US', {
    style: 'currency',
    currency: 'USD',
    maximumFractionDigits: 0,
  }).format(value)
}

export function strategyForKey(
  strategies: RecoveryStrategy[],
  key: RecoveryStrategyKey,
): RecoveryStrategy {
  const strategy = strategies.find((candidate) => candidate.key === key)
  if (!strategy) throw new Error(`The demo strategy "${key}" is not available for this incident.`)
  return strategy
}
