import type { RecoveryStrategy, RecoveryStrategyKey, SimulationScenario } from '../../types/simulation'

export function strategyForKey(scenario: SimulationScenario, key: RecoveryStrategyKey): RecoveryStrategy {
  const strategy = scenario.strategies.find((item) => item.key === key)
  if (!strategy) throw new Error(`Demo strategy "${key}" is unavailable for ${scenario.incident.id}.`)
  return strategy
}

export function formatCurrency(value: number): string {
  return new Intl.NumberFormat('en-US', { style: 'currency', currency: 'USD', maximumFractionDigits: 0 }).format(value)
}
