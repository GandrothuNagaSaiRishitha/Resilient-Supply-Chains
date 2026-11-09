import type { ApiResponse } from './api'
import type { CrisisType } from './crisisReport'
import type { RiskSeverity } from './impact'

export type RecoveryStrategyKey =
  | 'wait'
  | 'reroute'
  | 'emergency-sourcing'
  | 'redistribute'

export type FeasibilityStatus = 'Feasible' | 'Conditional' | 'Not feasible'

export interface SimulationIncident {
  id: string
  crisisType: CrisisType
  title: string
  reportedAt: string
}

export interface IncidentConstraint {
  id: string
  label: string
  detail: string
}

export interface RecoveryStrategy {
  key: RecoveryStrategyKey
  name: string
  summary: string
  additionalCost: number
  deliveryDelayDays: number
  projectedShortageUnits: number | null
  riskLevel: RiskSeverity
  feasibility: FeasibilityStatus
  feasibilityNote: string
  tradeOff: string
}

export interface CostDeliveryPoint {
  strategyKey: RecoveryStrategyKey
  strategyName: string
  additionalCost: number
  deliveryDelayDays: number
}

export interface SimulationScenario {
  incident: SimulationIncident
  summary: string
  constraints: IncidentConstraint[]
  strategies: RecoveryStrategy[]
  recommendedStrategyKey: RecoveryStrategyKey
  recommendationExplanation: string
  inventoryMapping?: { status: 'matched' | 'missing' | 'ambiguous'; reason: string; matchedSku: string | null }
}

export type SimulationIncidentsResponse = ApiResponse<SimulationIncident[]>
export type SimulationScenarioResponse = ApiResponse<SimulationScenario>

export interface ConfirmStrategyRequest {
  incidentId: string
  strategyKey: RecoveryStrategyKey
}

export interface ConfirmStrategyResponse {
  confirmationId: string
  incidentId: string
  strategyKey: RecoveryStrategyKey
  demo?: boolean
  message: string
}

export type ConfirmStrategyApiResponse = ApiResponse<ConfirmStrategyResponse>
