import type {
  RecoveryStrategyKey,
  SimulationIncident,
  SimulationScenario,
} from '../../types/simulation'
import type { ApiResponse } from '../../types/api'

export interface ReplayHistoricalEvidence {
  id: string
  incidentDate: string
  crisisType: string
  decision: string
  actualOutcome: string
  lesson: string
}

export interface ReplayActualOutcome {
  additionalCost: number
  deliveryDelayDays: number
  inventoryShortageUnits: number
  ordersAffected: number
  successful: boolean
  summary: string
}

export interface DecisionReplayRecord {
  incident: SimulationIncident
  scenario: SimulationScenario
  originalStrategyKey: RecoveryStrategyKey
  actualOutcome: ReplayActualOutcome
  memoryFreeStrategyKey: RecoveryStrategyKey
  memoryInformedStrategyKey: RecoveryStrategyKey | null
  memoryStatus?: 'available' | 'empty' | 'unavailable'
  historicalEvidence: ReplayHistoricalEvidence[]
  evidenceExplanation: string
  comparisonExplanation: string
}

export type DecisionReplayListResponse = ApiResponse<SimulationIncident[]>
export type DecisionReplayResponse = ApiResponse<DecisionReplayRecord>

export type ReplayActionResponse = ApiResponse<{
  incidentId: string
  replayed: boolean
  memoryStatus?: 'available' | 'empty' | 'unavailable'
  message: string
}>
