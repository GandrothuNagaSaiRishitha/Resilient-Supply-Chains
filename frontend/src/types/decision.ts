import type { ApiResponse } from './api'
import type {
  RecoveryStrategyKey,
  SimulationScenario,
} from './simulation'

export type DecisionAction = 'accepted' | 'rejected' | 'alternative'

export interface DecisionIncidentContext {
  description: string
  urgency: 'Low' | 'Medium' | 'High' | 'Critical'
  currentImpact: string
}

export interface HistoricalEvidence {
  id: string
  incidentDate: string
  crisisType: string
  previousStrategy: string
  outcome: string
  lessonLearned: string
  demoRecord?: boolean
}

export interface AlternativeStrategyContext {
  strategyKey: RecoveryStrategyKey
  whyLessSuitable: string
}

export interface MemoryComparison {
  memoryFreeStrategyKey: RecoveryStrategyKey
  memoryFreeExplanation: string
  memoryInformedStrategyKey: RecoveryStrategyKey
  memoryInformedExplanation: string
  evidenceIds: string[]
  whatChanged: string
}

export interface DecisionReport {
  scenario: SimulationScenario
  incidentContext: DecisionIncidentContext
  expectedBenefits: string[]
  risksAndTradeoffs: string[]
  executionConditions: string[]
  alternatives: AlternativeStrategyContext[]
  historicalEvidence: HistoricalEvidence[]
  memoryComparison: MemoryComparison
  demoDataNotice?: string
}

export type DecisionReportResponse = ApiResponse<DecisionReport>

export interface DecisionActionRequest {
  incidentId: string
  action: DecisionAction
  strategyKey: RecoveryStrategyKey | null
  explanation: string
}

export interface DecisionActionResponse {
  confirmationId: string
  demo?: boolean
  message: string
}

export type DecisionActionApiResponse = ApiResponse<DecisionActionResponse>

export interface OutcomeFeedbackRequest {
  incidentId: string
  strategyKey: RecoveryStrategyKey
  actualAdditionalCost: number
  actualDeliveryDelayDays: number
  actualInventoryShortage: number
  ordersAffected: number
  successful: boolean
  lessonsLearned: string
  additionalNotes: string
}

export interface OutcomeFeedbackResponse {
  outcomeId: string
  demo?: boolean
  message: string
}

export type OutcomeFeedbackApiResponse = ApiResponse<OutcomeFeedbackResponse>

export type DecisionIncidentsResponse = ApiResponse<SimulationScenario['incident'][]>
