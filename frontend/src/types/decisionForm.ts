import type { RecoveryStrategyKey } from './simulation'

export interface DecisionOutcomeValues {
  strategyKey: RecoveryStrategyKey | ''
  actualAdditionalCost: string
  actualDeliveryDelayDays: string
  actualInventoryShortage: string
  ordersAffected: string
  successful: '' | 'yes' | 'no'
  lessonsLearned: string
  additionalNotes: string
}
